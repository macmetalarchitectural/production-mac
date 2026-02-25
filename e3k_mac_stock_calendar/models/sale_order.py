# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('picking_ids.date_deadline')
    def _compute_commitment_date(self):
        """Override to compute commitment_date from outgoing pickings"""
        for order in self:
            if order.picking_ids:
                outgoing_pickings = order.picking_ids.filtered(
                    lambda p: p.picking_type_code == 'outgoing' and p.date_deadline
                )
                if outgoing_pickings:
                    order.commitment_date = max(outgoing_pickings.mapped('date_deadline'))
                else:
                    super()._compute_commitment_date()
            else:
                super()._compute_commitment_date()
