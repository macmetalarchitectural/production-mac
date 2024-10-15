# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"


    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)
    flexible_date = fields.Boolean(string='Flexible Date', default=False)

    @api.model
    def _action_get_value_from_x_delivery_pickup(self):
        for rec in self.search([]):
            if hasattr(rec, 'x_delivery_pickup'):
                rec.delivery_pickup = rec.x_delivery_pickup

