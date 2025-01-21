# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"

    date_deadline = fields.Datetime(
        "Deadline", readonly=True,
        compute='_e3k_compute_date_deadline',
        help="Date Promise to the customer on the top level document (SO/PO)")


    @api.depends('picking_id', 'picking_id.date_deadline')
    def _e3k_compute_date_deadline(self):
        for move in self:
            if move.picking_id and move.picking_id.sale_id:
                move.date_deadline = move.picking_id.date_deadline