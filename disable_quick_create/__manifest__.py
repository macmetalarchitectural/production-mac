# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

{
  'name': 'Disable Quick Create',
  'version': '15.0.1.0.0',
  'author': 'Savoir-faire Linux',
  'maintainer': 'Numigi',
  'website': 'https://www.numigi.com',
  'license': 'LGPL-3',
  'category': 'Web',
  'summary': 'Disable "quick create" for all and "create and edit for specific models',
  'depends': ['web'],
  'data': [
    'views/ir_model.xml',
  ],
  "assets": {
    'web.assets_common': [
      'disable_quick_create/static/src/js/disable_quick_create.js',
    ],
  },
  'installable': True,
}
