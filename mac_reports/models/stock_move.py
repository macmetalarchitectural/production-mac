# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import Counter, defaultdict

from odoo import _, api, fields, tools, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import OrderedSet, groupby
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

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

    def _get_aggregated_product_quantities(self, **kwargs):
        aggregated_move_lines = {}

        def get_aggregated_properties(move_line=False, move=False):
            move = move or move_line.move_id
            uom = move.product_uom or move_line.product_uom_id
            name = move.product_id.display_name
            description = move.description_picking
            if description == name or description == move.product_id.name:
                description = False
            product = move.product_id
            #j'ai ajouté move_line.id (id est unique pour chaque ligne pour empêcher de fusionner le même produits dans le BL
            if move_line:
                line_key = f'{product.id}_{product.display_name}_{description or ""}_{uom.id}_move_line{move_line.id}'
            else:
                line_key = f'{product.id}_{product.display_name}_{description or ""}_{uom.id}_move{move.id}'

            return (line_key, name, description, uom)

        # Loops to get backorders, backorders' backorders, and so and so...
        backorders = self.env['stock.picking']
        pickings = self.picking_id
        while pickings.backorder_ids:
            backorders |= pickings.backorder_ids
            pickings = pickings.backorder_ids

        for move_line in self:
            if kwargs.get('except_package') and move_line.result_package_id:
                continue
            line_key, name, description, uom = get_aggregated_properties(move_line=move_line)

            qty_done = move_line.product_uom_id._compute_quantity(move_line.qty_done, uom)

            if line_key not in aggregated_move_lines:
                qty_ordered = None
                if backorders and not kwargs.get('strict'):
                    qty_ordered = move_line.move_id.product_uom_qty
                    # Filters on the aggregation key (product, description and uom) to add the
                    # quantities delayed to backorders to retrieve the original ordered qty.
                    following_move_lines = backorders.move_line_ids.filtered(
                        lambda ml: get_aggregated_properties(move=ml.move_id)[0] == line_key
                    )
                    qty_ordered += sum(following_move_lines.move_id.mapped('product_uom_qty'))
                    # Remove the done quantities of the other move lines of the stock move
                    previous_move_lines = move_line.move_id.move_line_ids.filtered(
                        lambda ml: get_aggregated_properties(move=ml.move_id)[0] == line_key and ml.id != move_line.id
                    )
                    qty_ordered -= sum(map(lambda m: m.product_uom_id._compute_quantity(m.qty_done, uom), previous_move_lines))
                aggregated_move_lines[line_key] = {'name': name,
                                                   'description': description,
                                                   'qty_done': qty_done,
                                                   'qty_ordered': qty_ordered or qty_done,
                                                   'product_uom': uom.name,
                                                   'product_uom_rec': uom,
                                                   'product': move_line.product_id}
            else:
                aggregated_move_lines[line_key]['qty_ordered'] += qty_done
                aggregated_move_lines[line_key]['qty_done'] += qty_done

        # Does the same for empty move line to retrieve the ordered qty. for partially done moves
        # (as they are splitted when the transfer is done and empty moves don't have move lines).
        if kwargs.get('strict'):
            return aggregated_move_lines
        pickings = (self.picking_id | backorders)
        for empty_move in pickings.move_lines:
            if not (empty_move.state == "cancel" and empty_move.product_uom_qty
                    and float_is_zero(empty_move.quantity_done, precision_rounding=empty_move.product_uom.rounding)):
                continue
            line_key, name, description, uom = get_aggregated_properties(move=empty_move)

            if line_key not in aggregated_move_lines:
                qty_ordered = empty_move.product_uom_qty
                aggregated_move_lines[line_key] = {
                    'name': name,
                    'description': description,
                    'qty_done': False,
                    'qty_ordered': qty_ordered,
                    'product_uom': uom.name,
                    'product': empty_move.product_id,
                    'description': '',
                    'sale_line_id': False
                }
            else:
                aggregated_move_lines[line_key]['qty_ordered'] += empty_move.product_uom_qty


        #j'ai gardé l'ancien dev effectuer par Assia
        for move_line in self:
            line_key, name, description, uom = get_aggregated_properties(move_line=move_line)

            if self.move_id.sale_line_id:

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


