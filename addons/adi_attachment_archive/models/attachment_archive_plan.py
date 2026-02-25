# -*- coding: utf-8 -*-
import base64
import io
import logging
import os
import re
import shutil
import tarfile

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config, safe_eval

_logger = logging.getLogger(__name__)


class AttachmentArchivePlan(models.Model):
    """Defines a plan for archiving ir.attachment files to an external directory.

    Each plan targets a specific Odoo model (optionally filtered by a domain),
    and specifies a sub-folder path inside the server-level ``archive_dir``
    where matching attachment files will be physically moved.
    """

    _name = 'attachment.archive.plan'
    _description = 'Attachment Archive Plan'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='The Odoo model whose attachments should be archived.',
    )
    model_name = fields.Char(related='model_id.model', string='Model Name', store=True)
    domain = fields.Char(
        string='Domain Filter',
        default='[]',
        help='Optional domain to restrict which records in the selected model '
             'have their attachments archived. Leave as [] to archive all.',
    )
    archive_folder = fields.Char(
        string='Archive Sub-folder',
        required=True,
        help='Sub-folder path relative to archive_dir (configured in odoo.conf) '
             'where attachment files will be moved. E.g. "invoices/2026".',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        required=True,
    )
    last_run = fields.Datetime(string='Last Run', readonly=True)
    use_record_subfolder = fields.Boolean(
        string='Use Record Sub-folder',
        default=False,
        help='When enabled, each attachment is stored inside a child sub-folder named '
             'after the display name (complete_name) of the related record.',
    )
    attachment_count = fields.Integer(
        string='Archived Attachments',
        compute='_compute_attachment_count',
    )

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    @api.constrains('archive_folder')
    def _check_archive_folder(self):
        for plan in self:
            folder = plan.archive_folder or ''
            # Disallow absolute paths and path traversal sequences
            if os.path.isabs(folder) or '..' in folder.split(os.sep):
                raise ValidationError(_(
                    'Archive Sub-folder must be a relative path without ".." components. '
                    'Got: %s', folder
                ))

    # -------------------------------------------------------------------------
    # Compute helpers
    # -------------------------------------------------------------------------

    def _compute_attachment_count(self):
        for plan in self:
            plan.attachment_count = self.env['ir.attachment'].search_count(
                [('archive_plan_id', '=', plan.id)]
            )

    # -------------------------------------------------------------------------
    # State transitions
    # -------------------------------------------------------------------------

    def action_activate(self):
        self.write({'state': 'active'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_mark_done(self):
        self.write({'state': 'done'})

    # -------------------------------------------------------------------------
    # Archiving logic
    # -------------------------------------------------------------------------

    def _get_archive_dir(self):
        """Return the configured archive_dir, raising an error if not set."""
        archive_dir = config.get('archive_dir', '')
        if not archive_dir:
            raise UserError(_(
                'The archive_dir option is not configured in odoo.conf. '
                'Please add "archive_dir = /path/to/archive" and restart the server.'
            ))
        return archive_dir

    @staticmethod
    def _sanitize_folder_name(name):
        """Sanitize a string so it can be safely used as a filesystem folder name."""
        # Replace path separators and reserved characters
        sanitized = re.sub(r'[/\\<>:"|?*\x00-\x1f]', '_', name or 'unknown')
        # Strip leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        return sanitized or 'unknown'

    def action_run_archive(self):
        """Execute this archiving plan: move matching attachment files to the archive."""
        self.ensure_one()
        if self.state not in ('active',):
            raise UserError(_('Only active plans can be executed.'))

        archive_dir = self._get_archive_dir()
        filestore = config.filestore(self.env.cr.dbname)

        # 1. Resolve the domain and find matching records
        domain = safe_eval.safe_eval(self.domain or '[]')
        try:
            target_records = self.env[self.model_name].search(domain)
        except Exception as exc:
            raise UserError(
                _('Invalid domain for model %(model)s: %(error)s',
                  model=self.model_name, error=str(exc))
            ) from exc

        if not target_records:
            self.last_run = fields.Datetime.now()
            return

        # 2. Build a display_name map when sub-folder by record is requested
        record_name_map = {}
        if self.use_record_subfolder:
            for rec in target_records:
                name = getattr(rec, 'complete_name', None) or rec.display_name or str(rec.id)
                record_name_map[rec.id] = self._sanitize_folder_name(name)

        # 3. Find attachments that have not yet been archived
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self.model_name),
            ('res_id', 'in', target_records.ids),
            ('store_fname', '!=', False),
            ('archive_plan_id', '=', False),
        ])

        # Pre-compute and validate the destination base path
        real_archive = os.path.realpath(archive_dir)
        dest_base = os.path.realpath(os.path.join(archive_dir, self.archive_folder))
        if not dest_base.startswith(real_archive + os.sep):
            raise UserError(_(
                'The archive sub-folder "%s" resolves outside of archive_dir. '
                'Please use a relative path without ".." components.',
                self.archive_folder,
            ))

        archived = 0
        for attachment in attachments:
            src_path = os.path.join(filestore, attachment.store_fname)
            if not os.path.isfile(src_path):
                _logger.warning(
                    'Attachment %s: source file not found at %s, skipping.',
                    attachment.id, src_path,
                )
                continue

            # Determine effective destination folder for this attachment
            if self.use_record_subfolder and attachment.res_id in record_name_map:
                record_subfolder = record_name_map[attachment.res_id]
                effective_folder = os.path.join(self.archive_folder, record_subfolder)
                effective_dest_base = os.path.join(dest_base, record_subfolder)
            else:
                effective_folder = self.archive_folder
                effective_dest_base = dest_base

            # Compute destination path preserving the hash-based sub-directory
            dest_path = os.path.join(effective_dest_base, attachment.store_fname)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)

            try:
                shutil.move(src_path, dest_path)
            except OSError:
                _logger.exception(
                    'Failed to move attachment %s from %s to %s.',
                    attachment.id, src_path, dest_path,
                )
                continue

            # Update the attachment record.  Store the effective_folder so that
            # _file_read can reconstruct the exact path later.
            attachment.sudo().write({
                'archive_plan_id': self.id,
                'archive_folder': effective_folder,
            })
            archived += 1

        self.last_run = fields.Datetime.now()
        _logger.info(
            'Archive plan "%s" completed: %d attachment(s) archived.', self.name, archived
        )
        return archived

    # -------------------------------------------------------------------------
    # Download archive as tar.gz
    # -------------------------------------------------------------------------

    def action_download_archive(self):
        """Compress the archive folder for this plan and return a file download."""
        self.ensure_one()
        archive_dir = self._get_archive_dir()
        folder_path = os.path.join(archive_dir, self.archive_folder)

        if not os.path.isdir(folder_path) or not os.listdir(folder_path):
            raise UserError(_(
                'Archive folder "%s" does not exist or is empty.', folder_path
            ))

        # Build the tar.gz in memory
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode='w:gz') as tar:
            tar.add(folder_path, arcname=self._sanitize_folder_name(self.archive_folder))
        buf.seek(0)
        tar_bytes = buf.read()

        # Store as a temporary attachment and redirect to download
        filename = '%s.tar.gz' % self._sanitize_folder_name(self.archive_folder)
        attachment = self.env['ir.attachment'].sudo().create({
            'name': filename,
            'datas': base64.b64encode(tar_bytes),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % attachment.id,
            'target': 'self',
        }

    # -------------------------------------------------------------------------
    # Scheduled action entry point
    # -------------------------------------------------------------------------

    def action_view_archived_attachments(self):
        """Open the list of attachments archived by this plan."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Archived Attachments'),
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('archive_plan_id', '=', self.id)],
            'context': {'default_archive_plan_id': self.id},
        }

    @api.model
    def _cron_run_archive_plans(self):
        """Run all active archive plans. Called by the daily scheduler."""
        plans = self.search([('state', '=', 'active')])
        for plan in plans:
            try:
                plan.action_run_archive()
            except Exception:
                _logger.exception(
                    'Error while running attachment archive plan "%s" (id=%d).',
                    plan.name, plan.id,
                )
