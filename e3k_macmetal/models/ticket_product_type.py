# -*- coding: utf-8 -*-

from odoo import fields, models


class E3kTicketProductType(models.Model):
    _name = "e3k.ticket.product.type"
    _description = "Ticket Product Type"
    _order = "name"

    name = fields.Char(string="Name", required=True, translate=True)
