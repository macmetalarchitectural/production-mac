# -*- coding: utf-8 -*-
{
    'name': "e3k_Mac_contact_customisation",
    'summary': "MAC Metal contact customisation",
    'license': 'LGPL-3',
    'author': "e3k",
    'website': "https://e3k.co",
    'category': 'Uncategorized',
    'version': '19.0.6',
    'depends': ['l10n_ca', 'mail', 'e3k_macmetal', 'partner_validation_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/contact_status.xml',
        'views/reprentative_team.xml',
        'views/calendar_event.xml',
        'data/contact_status.xml',
        'data/ir_sequence.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'e3k_mac_contact_customisation/static/src/**/*',
        ],
    },
}
