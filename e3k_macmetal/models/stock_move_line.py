# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    note = fields.Char('Note')  # no-check
    e3k_lot_ref = fields.Char(
        string='Internal Reference',
    )

    def _prepare_new_lot_vals(self):
        vals = super()._prepare_new_lot_vals()
        if self.e3k_lot_ref:
            vals['ref'] = self.e3k_lot_ref
        return vals
