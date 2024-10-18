# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"


    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)
    flexible_date = fields.Boolean(string='Flexible Date', default=False)
    e3k_all_day = fields.Boolean(string='All Day', default=True)

    @api.model
    def _action_get_value_from_x_delivery_pickup(self):
        # fonction a executer une seule fois pour mettre a jour les valeurs
        for rec in self.search([]):
            if hasattr(rec, 'x_delivery_pickup'):
                rec.delivery_pickup = rec.x_delivery_pickup

