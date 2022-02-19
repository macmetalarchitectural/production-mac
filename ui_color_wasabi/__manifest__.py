# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
  "name": "UI Color Wasabi",
  'version': '15.0.1.0.0',
  'author': 'Numigi',
  'maintainer': 'Numigi',
  'website': 'https://bit.ly/numigi-com',
  'license': 'LGPL-3',
  "category": "Web Interface",
  "summary": "Render The Odoo Enterprise Interface Unique",
  "depends": ['web_enterprise'],
  "assets": {
    'web._assets_primary_variables': [
      ('after', 'web_enterprise/static/src/legacy/scss/primary_variables.scss', 'ui_color_wasabi/static/src/scss/primary_variables.scss'),
    ],
    'web._assets_common_styles': [
      'ui_color_wasabi/static/src/scss/custom.scss',
    ],
  },
  "installable": True,
}
