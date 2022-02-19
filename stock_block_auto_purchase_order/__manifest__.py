# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Block Auto Purchase Order',
    'version': '1.0',
    'category': 'Purchase',
    'description': 'Use a boolean to prevent the automatic make of Purchase Order.',
    'maintainer': 'numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
    ],
}
