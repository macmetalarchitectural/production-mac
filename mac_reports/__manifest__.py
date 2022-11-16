# -*- coding: utf-8 -*-
{
    'name': "E3k Mac Reports",
    'summary': """
        """,
    'description': """
    """,
    'author': "E3K",
    'website': "http://www.e3k.co",
    'category': 'Sale',
    'version': '15.1',
    'depends': ['e3k_default_reports', 'account'],
    'data': [
        'reports/sale_report.xml',
        'reports/invoice_report.xml',
        'reports/delivery_slip.xml',
        'reports/report_picking.xml',
        'reports/purachse_order.xml',
        'views/sale_order.xml',
        'views/picking_form_view.xml',
    ],
    'demo': [
    ],
}
