# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Product Paint Batch',
    'version': '10.0.1.0.0',
    'author': 'Numigi (TM)',
    'maintainer': 'Numigi (TM)',
    'website': 'http://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Product',
    'summary': 'Add the management of batch of paint in product',
    'depends': [
        'stock',
    ],
    'data': [
        'views/stock_production_lot.xml',
        'views/product.xml',
    ],
    'installable': True,
}
