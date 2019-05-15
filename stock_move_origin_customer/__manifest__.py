# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Stock Move Origin Customer',
    'version': '1.0.0',
    'category': 'Stock',
    'summary': "Add the partner name that is at the origin of the stock move.",
    'author': 'Numigi',
    'depends': ['stock', 'purchase', 'sale'],
    'data': [
        'stock_move.xml',
    ],
    'application': False,
}
