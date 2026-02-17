# -*- coding: utf-8 -*-
{
    'name': 'Custom Payment Cheque',
    'summary': 'Custom Payment Cheque',
    'version': '1.0.2',
    'category': 'account',
    'author': "e3k",
    'website': "https://e3k.co",
    'depends': ['l10n_ca_check_printing'],
    'data': [
        # Reports
        'report/print_check_top.xml',
        'report/report_payment_receipt_templates.xml',
        'report/ckca_check.xml',
        # Views
        'views/company.xml',
        'views/journal.xml',
        'views/account_payment_register_views.xml',
        'views/account_payment_views.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            '/e3k_custom_cheque/static/src/less/report_check_commons.less',
        ],
        'web.assets_backend': [
            '/e3k_custom_cheque/static/src/css/account_payment_style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
