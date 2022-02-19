# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductWithPaintType(models.Model):

    _inherit = 'product.product'

    paint_type = fields.Char('Paint Type', compute='_compute_paint_type')

    def _compute_paint_type(self):
        for product in self:
            paint_types = product.mapped('attribute_value_ids.paint_type')
            product.paint_type = ', '.join(t for t in paint_types if t)
