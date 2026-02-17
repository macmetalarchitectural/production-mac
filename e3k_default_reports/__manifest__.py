# -*- coding: utf-8 -*-
{
    'name': "Default Reports",
    'summary': """
        This module should be installed at all projects by default as it contains
        all common transformations of Odoo Pdf reports
    """,
    'author': "e3k",
    'license': 'LGPL-3',
    'website': "https://www.e3k.co",
    'category': 'Uncategorized',
    'version': '1.0.3',
    'depends': ['sale_management', 'sale_stock', 'purchase', 'delivery'],
    'data': [
        'wizard/res_config_settings_view.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_template.xml',
        'views/ir_action_report.xml',
        'reports/invoice_report.xml',
        'reports/sale_report.xml',
        'reports/purchase_order.xml',
        'reports/delivery_slip.xml',
        'reports/tax_report.xml',
        'reports/sale_order_portal_content.xml',
    ],
}
