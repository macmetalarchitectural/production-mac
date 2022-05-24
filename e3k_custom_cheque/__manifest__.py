# -*- coding: utf-8 -*-

{
    'name': 'Custom Payment Cheque',
    'description': 'Custom Payment Cheque',
    'version': '15.0.0.0.0',
    'category': 'account',
    'author': "E3K",
    'depends': ['account', 'l10n_ca_check_printing','e3k_advanced_payment'],
    'data': [
        'views/company.xml',
        'views/journal.xml',
        'report/print_check_top.xml',
        'report/report_payment_receipt_templates.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            '/e3k_custom_cheque/static/src/less/report_check_commons.less',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
