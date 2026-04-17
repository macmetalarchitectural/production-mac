# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_po(self):
        for rec in self:
            purchases = " "
            for purchase in rec.picking_id.sale_id._get_purchase_orders():
                if rec.product_id in purchase.order_line.mapped('product_id'):
                    purchases = purchases + " " + purchase.name
            return purchases


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_aggregated_properties(self, move_line=False, move=False):
        res = super()._get_aggregated_properties(move_line=move_line, move=move)
        # Add move_line.id to key to prevent aggregation of same products
        if move_line:
            res['line_key'] += f'_move_line{move_line.id}'
        return res

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)

        # Add sale_line_id and use sale_line description when available
        for move_line in self:
            aggregated_properties = self._get_aggregated_properties(move_line=move_line)
            line_key = aggregated_properties['line_key']

            if line_key not in aggregated_move_lines:
                continue

            if move_line.move_id.sale_line_id:
                aggregated_move_lines[line_key]['description'] = move_line.move_id.sale_line_id.name
                aggregated_move_lines[line_key]['sale_line_id'] = move_line.move_id.sale_line_id
            else:
                aggregated_move_lines[line_key]['sale_line_id'] = False

        return aggregated_move_lines

    def get_po(self):
        for rec in self:
            purchases = " "
            for purchase in rec.move_id.picking_id.sale_id._get_purchase_orders():
                _logger.info(purchase.order_line.mapped('product_id'))
                if rec.product_id in purchase.order_line.mapped('product_id'):
                    purchases = purchases + " " + purchase.name
            return purchases