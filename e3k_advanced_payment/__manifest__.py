# -*- coding: utf-8 -*-

{
    'name': 'E3K Advanced Payment',
    'description': 'Select invoices when paying a supplier.',
    'author': "E3K",
    'website': "https://e3kco.odoo.com",
    'version': '15.0.1',
    'category': 'Accounting/Payment',
    'depends': ['account', 'account_check_printing', 'account_accountant'],

    'data': [
        'security/ir.model.access.csv',
        'data/email_templat.xml',
        'wizard/send_statement_message.xml',

        'views/account_payment.xml',
        'views/payment_term.xml',
        'views/account_move.xml',
        'views/account_settings.xml',
        'views/partial_payment.xml',
        'report/report_invoice.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
