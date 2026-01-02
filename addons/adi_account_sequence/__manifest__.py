# -*- coding: utf-8 -*-
{
    'name': 'ADI Account Sequence with Goods Type',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Custom sequence format with goods_type field for invoices',
    'description': """
ADI Account Sequence Extension
===============================

Extends the Odoo accounting sequence mixin to support custom fields (like goods_type) in sequence formats.

Features:
---------
* Adds goods_type field to account.move
* Supports custom sequence formats like: AD-SI-L-2601-01-0001
  - AD-SI-L- = Fixed prefix
  - 2601 = Year-Month (YYMM)
  - 01 = Goods Type (custom field)
  - 0001 = 4-digit sequence

* Automatic sequence reset when:
  - Month changes
  - Goods type changes

* Each year-month-goods_type combination maintains independent counter
* Fully backward compatible with existing sequences

Usage:
------
1. Configure journal's sequence_override_regex to include goods_type capture group
2. Set goods_type field on invoices
3. System automatically generates sequences following the pattern

See documentation files for detailed usage instructions.
    """,
    'author': 'ADI',
    'website': 'https://github.com/hendrasaputra0501/odoo-18',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
