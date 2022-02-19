# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
  _inherit = 'res.config.settings'

  delivery_terms = fields.Html(string='Default Delivery Terms & Conditions', related='company_id.delivery_terms', readonly=False)
  use_delivery_terms = fields.Boolean(
    string='Delivery Default Terms & Conditions',
    config_parameter='e3k_macmetal.use_delivery_terms',
    default=False)

