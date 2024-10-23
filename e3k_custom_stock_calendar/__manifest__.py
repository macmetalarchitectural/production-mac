# -*- coding: utf-8 -*-
{
    'name': 'E3K Custom Stock Calendar',
    'version': '1.0.1',
    'author': 'e3k solutions',
    'maintainer': 'e3k',
    'website': 'https://www.e3k.co/',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'E3K Custom Stock Calendar',
    'depends': ['e3k_macmetal'],
    'data': [
        # data

        # security

        # views
        'views/stock_picking.xml',

        # wizard
    ],
    'assets': {
        'web.assets_qweb': [
            'e3k_custom_stock_calendar/static/src/legacy/xml/template.xml',
        ],
        'web.assets_backend': [
            'e3k_custom_stock_calendar/static/src/legacy/js/views/calendar/calendar_renderer.js',
        ],
    },
    'installable': True,
    'application': False,
}
