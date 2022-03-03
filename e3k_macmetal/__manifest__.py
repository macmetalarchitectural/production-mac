# -*- coding: utf-8 -*-

{
  "name" : "e3k MACMÉTAL",
  "summary" : "",
  "description" : "",
  "category" : "Sales/Sales",
  "author" : "e3k Solutions",
  "license" : "Other proprietary",
  "website" : "https://e3k.co",
  "version" : "15.0.1.0.2",
  "depends" : [
    'sale',
    'crm',
    'calendar',
    'stock',
  ],
  "data" : [
    'views/res_config_settings_views.xml',
    'views/sale_portal_templates.xml',
    'views/sale_views.xml',
    'views/stock_quant_views.xml',
    'views/stock_move_line_views.xml',
    'views/calendar_views.xml',
    'views/stock_location_views.xml',
  ],
  'assets': {
    'web.assets_frontend': [
      'web/static/src/legacy/js/fields/field_utils.js',
      'e3k_macmetal/static/src/js/signature_form.js',
    ],
  },
  "images" : [],
  "application" : False,
  "installable" : True,
  "auto_install" : False,
  "pre_init_hook" : "pre_init_check",
}