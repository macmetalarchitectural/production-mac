# -*- coding: utf-8 -*-

from odoo import fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    date_deadline = fields.Datetime(
        "Deadline", readonly=True,
        related='picking_id.date_deadline',
        help="Date Promise to the customer on the top level document (SO/PO)")