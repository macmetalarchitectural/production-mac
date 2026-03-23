# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    e3k_division_id = fields.Many2one(  # no-check
        "res.partner",
        string="Division",
    )
    e3k_inside_sales_rep_id = fields.Many2one(  # no-check
        "res.users",
        string="Inside Sales Rep",
        help="The order desk employee who is responsible for the client account.",
    )
    e3k_maison_mere_id = fields.Many2one(  # no-check
        "res.partner",
        string="Parent Company",
    )
