# -*- coding: utf-8 -*-
{
    'name': "E3k Default Reports",
    'summary': """
        This module should be installed at all projects by default as it contains all common
        transformations of Odoo Pdf reports """,
    'description': """

    """,
    'author': "E3K",
    'license': 'LGPL-3',
    'website': "http://www.e3k.co",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['account', 'sale', 'sale_stock', 'purchase'],
    'data': [
        'wizard/res_config_settings_view.xml',
        'views/sale_order_view.xml',
        #'views/account_move_view.xml',
        'reports/external_layout.xml',
        'reports/invoice_report.xml',
        'reports/sale_report.xml',
        'reports/purchase_order.xml',
        'reports/delivery_slip.xml',
    ],
    'application': True,
    'installable': True,
}
