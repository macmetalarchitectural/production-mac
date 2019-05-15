# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models, fields, api


class StockProductionLotWithPaintBatch(models.Model):
    """Add the field paint_batch"""
    _inherit = 'stock.production.lot'

    # see TA#1778
    paint_batch = fields.Char(string='Paint Batch', compute='_paint_batch', store=True)

    @api.depends('product_id.paint_batch_track', 'name')
    def _paint_batch (self):
        length = int(self.env['ir.config_parameter'].sudo().get_param('product_paint_batch.paint_batch_length'))
        for record in self:
            if record.product_id.paint_batch_track:
                record.paint_batch = record.name[:length]
            else:
                record.paint_batch = None
