# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    e3k_date_field = fields.Date(string="New Date")  # no-check
