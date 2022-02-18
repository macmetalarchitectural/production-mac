# Copyright (C) 2013 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
  "name": "Remove odoo.com Bindings",
  "version": "15.0.1.0.0",
  "author": "Therp BV,GRAP,Odoo Community Association (OCA)",
  "website": "https://github.com/OCA/server-brand",
  "license": "AGPL-3",
  "category": "base",
  "depends": ["mail"],
  "data": ["views/ir_ui_menu.xml"],
  'assets': {
    'web.assets_backend': [
      'disable_odoo_online/static/src/js/user_menu_items.js',
    ],
  },
  "installable": True,
}
