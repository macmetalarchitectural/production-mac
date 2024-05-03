# -*- coding: utf-8 -*-
{
    'name': "e3k_Mac_contact_customisation",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
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
            'e3k_mac_contact_customisation/static/src/js/schedule_meeting.js',
            'e3k_mac_contact_customisation/static/src/js/schedule_next.js',
            'e3k_mac_contact_customisation/static/src/js/activity_dashboard.js',
            'e3k_mac_contact_customisation/static/src/js/remove_option.js',
            'e3k_mac_contact_customisation/static/src/css/style.css',

        ],
        'web.assets_qweb': [
            'e3k_mac_contact_customisation/static/src/xml/contact_chatter.xml',
            'e3k_mac_contact_customisation/static/src/xml/activity_dashboard.xml',
        ],
    },
}
