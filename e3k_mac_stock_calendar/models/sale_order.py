# -*- coding: utf-8 -*-

from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date = fields.Datetime(compute='_compute_commitment_date', readonly=False, store=True, )

    @api.depends('picking_ids.date_deadline')
    def _compute_commitment_date(self):
        for order in self:
            if order.picking_ids:
                order.commitment_date = max(order.picking_ids.mapped('date_deadline'), default=False)
            else:
                pass