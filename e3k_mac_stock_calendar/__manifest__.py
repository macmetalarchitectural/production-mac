# -*- coding: utf-8 -*-
{
    'name': 'E3K Stock Calendar',
    'version': '19.0.1',
    'author': 'e3k',
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
        'web.assets_backend': [
            'e3k_mac_stock_calendar/static/src/views/calendar/stock_calendar_common_renderer.js',
            'e3k_mac_stock_calendar/static/src/views/calendar/stock_calendar_common_renderer.xml',
            'e3k_mac_stock_calendar/static/src/scss/stock_calendar.scss',
        ],
        'web.assets_backend_lazy_dark': [
            'e3k_mac_stock_calendar/static/src/scss/stock_calendar.dark.scss',
        ],
    },
    'installable': True,
    'application': False,
    # "post_init_hook": "_post_init_hook",
}
