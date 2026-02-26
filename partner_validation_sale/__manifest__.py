# © 2018 Akretion
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Partner Validation Sale',
    'version': '19.0.1',
    'author': 'e3k',
    'website': 'https://e3k.co',
    'license': 'LGPL-3',
    'category': 'Partner Management',
    'depends': [
        'partner_validation',
        'sale_stock',
    ],
    'data': [
        'security/res_groups.xml',
        'views/res_partner_restricted_field.xml',
        'views/res_partner.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'partner_validation_sale/static/src/**/*',
        ],
    },
    'application': False,
    'installable': True,
}
