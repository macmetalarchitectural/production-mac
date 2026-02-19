# -*- coding: utf-8 -*-

from odoo import fields, models

class Location(models.Model):
  _inherit = "stock.location"

  show_loc_inv_adj = fields.Boolean('Show Location in Inventory Adjustments', default=True)