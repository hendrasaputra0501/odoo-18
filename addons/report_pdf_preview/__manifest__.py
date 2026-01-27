# -*- coding: utf-8 -*-
{
    'name': 'Report PDF Preview',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Preview PDF Reports in Dialog Box',
    'description': """
Report PDF Preview
==================
This module displays a Dialog Box with an iframe when users print a qweb-pdf report,
allowing them to preview the PDF before downloading.
    """,
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'report_pdf_preview/static/src/js/pdf_preview_dialog.js',
            'report_pdf_preview/static/src/xml/pdf_preview_dialog.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
