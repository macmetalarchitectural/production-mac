# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_po(self):
        for rec in self:
            purchases = " "
            for purchase in rec.sale_line_id.order_id._get_purchase_orders():
                if rec.product_id in purchase.order_line.mapped('product_id'):
                    purchases = purchases + " " + purchase.name




class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def get_po(self):
        for rec in self:
            purchases = ""
            for purchase in rec.move_id.sale_line_id.order_id._get_purchase_orders():
                if rec.product_id in purchase.order_line.mapped('product_id'):
                    purchases += purchase.name