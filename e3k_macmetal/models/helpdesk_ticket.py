# -*- coding: utf-8 -*-

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    e3k_old_amount = fields.Char(string="Old Amount")  # no-check
    e3k_amount = fields.Float(string="Amount")  # no-check
    e3k_ticket_product_type_id = fields.Many2one(  # no-check
        "e3k.ticket.product.type",
        string="Product Type",
    )
