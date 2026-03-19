# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    e3k_drawing = fields.Html(  # no-check
        string="Drawing",
        related="product_id.product_tmpl_id.e3k_drawing",
        readonly=True,
    )
