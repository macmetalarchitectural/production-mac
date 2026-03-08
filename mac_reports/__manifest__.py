# -*- coding: utf-8 -*-
{
    'name': "E3k Mac Reports",
    'summary': """
        """,
    'description': """
    """,
    'license': 'LGPL-3',
    'author': "E3K",
    'website': "http://www.e3k.co",
    'category': 'Sale',
    'version': '19.0.1.0.0',
    'depends': ['e3k_default_reports', 'account', 'stock_delivery'],
    'data': [
        'reports/sale_report.xml',
        'reports/invoice_report.xml',
        'reports/delivery_slip.xml',
        'reports/report_picking.xml',
        'reports/purachse_order.xml',
        'reports/report_delivery_document.xml',
        'views/sale_order.xml',
        'views/picking_form_view.xml',
    ],
    'demo': [
    ],
}
