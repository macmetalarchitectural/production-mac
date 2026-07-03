# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    note = fields.Char('Note')  # no-check
    e3k_lot_ref = fields.Char(
        string='Internal Reference',
        compute='_compute_e3k_lot_ref',
        inverse='_inverse_e3k_lot_ref',
    )

    @api.depends('lot_id.ref')
    def _compute_e3k_lot_ref(self):
        for line in self:
            line.e3k_lot_ref = line.lot_id.ref

    def _inverse_e3k_lot_ref(self):
        for line in self:
            if line.lot_id:
                line.lot_id.ref = line.e3k_lot_ref

    def _prepare_new_lot_vals(self):
        vals = super()._prepare_new_lot_vals()
        if self.e3k_lot_ref:
            vals['ref'] = self.e3k_lot_ref
        return vals
