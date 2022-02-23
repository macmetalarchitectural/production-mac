# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_po(self):
        for rec in self:
            purchases = " "
            for purchase in rec.picking_id.sale_id._get_purchase_orders():
                _logger.info(purchase.order_line.mapped('product_id'))
                if rec.product_id in purchase.order_line.mapped('product_id'):
                    _logger.info(rec.product_id)
                    purchases = purchases + " " + purchase.name
            return purchases


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def get_po(self):
        for rec in self:
            purchases = " "
            for purchase in rec.move_id.picking_id.sale_id._get_purchase_orders():
                _logger.info(purchase.order_line.mapped('product_id'))
                if rec.product_id in purchase.order_line.mapped('product_id'):
                    _logger.info(rec.product_id)
                    purchases = purchases + " " + purchase.name
            return purchases