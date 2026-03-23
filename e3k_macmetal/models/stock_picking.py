# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)  # no-check
    e3k_delivery_on_hold = fields.Boolean(  # no-check
        string="Delivery On Hold",
        default=False,
    )
    e3k_currency_id = fields.Many2one(  # no-check
        related="company_id.currency_id",
    )
    e3k_sales_value = fields.Monetary(  # no-check
        string="Sales Value",
        currency_field="e3k_currency_id",
        readonly=True,
    )
