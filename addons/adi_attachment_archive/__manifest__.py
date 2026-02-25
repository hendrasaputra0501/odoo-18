# -*- coding: utf-8 -*-
{
    'name': 'ADI Attachment Archive',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Archive attachment files from filestore to an external archive directory',
    'description': """
ADI Attachment Archive
======================

Provides a mechanism to move attachment files stored in Odoo's filestore to a
separate archive directory (configurable via ``archive_dir`` in ``odoo.conf``).

Features:
---------
* Define **archive plans** that target a specific model, optionally filtered by
  a domain on that model's records.
* Each plan specifies a sub-folder path inside the ``archive_dir`` where the
  matching attachment files will be physically moved.
* A daily **scheduled action** executes all active plans automatically.
* Archived files remain fully accessible through the normal Odoo attachment
  interface.

Configuration:
--------------
Add the following line to your ``odoo.conf``::

    archive_dir = /mnt/archive

Usage:
------
1. Install this module.
2. Set ``archive_dir`` in ``odoo.conf`` and restart the server.
3. Go to **Technical → Attachments → Archive Plans** to create plans.
4. Activate plans; they will run daily or can be triggered manually.
    """,
    'author': 'ADI',
    'website': 'https://github.com/hendrasaputra0501/odoo-18',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/attachment_archive_plan_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
