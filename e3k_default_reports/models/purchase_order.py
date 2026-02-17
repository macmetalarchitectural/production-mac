# -*- coding: utf-8 -*-
import re

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    ref_seller_product_code = fields.Char('Vendor Product Code', compute="_compute_ref_seller_product_code")  # no-check
    has_seller_code = fields.Char('has seller  Code', compute="_compute_ref_seller_product_code")  # no-check

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)
        return None

    def _compute_ref_seller_product_code(self):
        for line in self:
            line.ref_seller_product_code = ' '
            line.has_seller_code = False

            if not line.partner_id:
                continue

            partner_prices = line.product_id.seller_ids.filtered(
                lambda r: r.partner_id == line.order_id.partner_id and r.product_code
            )
            if partner_prices:
                price = partner_prices[0]
                line.ref_seller_product_code += str(price.product_code)
                line.has_seller_code = True
