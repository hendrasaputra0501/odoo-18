# -*- coding: utf-8 -*-
import logging
import os
import re

from odoo import fields, models
from odoo.tools import config

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    """Extend ir.attachment to support external archive storage."""

    _inherit = 'ir.attachment'

    archive_plan_id = fields.Many2one(
        'attachment.archive.plan',
        string='Archive Plan',
        ondelete='set null',
        index=True,
        readonly=True,
        help='The archive plan that moved this file to the external archive directory.',
    )
    archive_folder = fields.Char(
        string='Archive Sub-folder',
        readonly=True,
        help='Sub-folder within archive_dir where this attachment file is stored.',
    )

    # -------------------------------------------------------------------------
    # File-read override
    # -------------------------------------------------------------------------

    def _file_read(self, fname, size=None):
        """Read the file content.

        If the attachment has been archived (``archive_folder`` is set), the
        file is read from the external archive directory instead of the normal
        filestore.
        """
        if self.archive_folder:
            archive_dir = config.get('archive_dir', '')
            if not archive_dir:
                _logger.error(
                    'Attachment %s is archived but archive_dir is not configured.',
                    self.id,
                )
                return b''
            # Use the same sanitisation as ir.attachment._full_path
            fname_safe = re.sub('[.:]', '', fname).strip('/\\')
            folder_safe = re.sub('[.:]', '', self.archive_folder).strip('/\\')
            full_path = os.path.join(archive_dir, folder_safe, fname_safe)
            # Guard against any remaining traversal
            real_archive = os.path.realpath(archive_dir)
            if not os.path.realpath(full_path).startswith(real_archive + os.sep):
                _logger.error(
                    '_file_read: path %s escapes archive_dir, refusing to read.',
                    full_path,
                )
                return b''
            try:
                with open(full_path, 'rb') as f:
                    return f.read(size)
            except OSError:
                _logger.info(
                    '_file_read: could not read archived file %s', full_path, exc_info=True
                )
                return b''
        return super()._file_read(fname, size=size)

    # -------------------------------------------------------------------------
    # Unlink override – also remove archived files
    # -------------------------------------------------------------------------

    def unlink(self):
        """Delete the record and, if the file is archived, also delete it from
        the external archive directory."""
        archive_dir = config.get('archive_dir', '')
        # Pre-collect archived file paths before deletion
        archived_paths = []
        if archive_dir:
            real_archive = os.path.realpath(archive_dir)
            for attachment in self:
                if attachment.archive_folder and attachment.store_fname:
                    fname_safe = re.sub('[.:]', '', attachment.store_fname).strip('/\\')
                    folder_safe = re.sub('[.:]', '', attachment.archive_folder).strip('/\\')
                    full_path = os.path.join(archive_dir, folder_safe, fname_safe)
                    if os.path.realpath(full_path).startswith(real_archive + os.sep):
                        archived_paths.append(full_path)

        res = super().unlink()

        for full_path in archived_paths:
            try:
                os.unlink(full_path)
            except OSError:
                _logger.info(
                    'Could not delete archived file %s', full_path, exc_info=True
                )
        return res
