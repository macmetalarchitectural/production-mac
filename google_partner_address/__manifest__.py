# © 2017-2018 Savoir-faire Linux
# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
  'name': 'Google Partner Address',
  'version': '15.0.1.0.0',
  'author': 'Savoir-faire Linux',
  'maintainer': 'Numigi',
  'website': 'https://www.numigi.com',
  'license': 'LGPL-3',
  'category': 'Partner Management',
  'summary': 'Add address assisted selection',
  'depends': ['base_setup'],
  'data': [
    'views/res_config_settings.xml',
    'views/res_partner.xml',
  ],
  "assets": {
    'web.assets_backend': [
      'google_partner_address/static/src/js/google_partner_address.js',
      'google_partner_address/static/src/scss/google_partner_address.scss',
    ],
  },
  'installable': True,
}
