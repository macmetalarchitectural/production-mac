# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Aged Partner Balance Invoice Date',
    'version': '1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'summary': 'Add advanced options to partner aged balances',
    'depends': [
        'account_reports',
    ],
    'data': [
        'assets.xml',
        'templates.xml',
    ],
    'installable': True,
}
