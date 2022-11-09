# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    note = fields.Html('Notes', default='<p style="font-size: 18px; font-weight: bold;"><br></p>')
