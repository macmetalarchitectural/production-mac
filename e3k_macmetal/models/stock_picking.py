# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)  # no-check
