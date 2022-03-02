# -*- coding: utf-8 -*-

{
    'name': 'Custom Payment Cheque',
    'description': 'Custom Payment Cheque',
    'version': '15.0.1',
    'category': 'account',
    'author': "E3k Solutions",
    'depends': ['account', 'l10n_ca_check_printing'],
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
