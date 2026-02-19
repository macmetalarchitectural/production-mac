# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    delivery_terms = fields.Html(
        string="Delivery Default Terms and Conditions",
        translate=True,
        default="""
            <h1 style="text-align: center; ">Delivery Terms &amp; Conditions</h1>
            <p>Your conditions...</p>
        """,
    )
    padding_delivery_days = fields.Integer(
        string="Padding Delivery Days",
        help="Amount of days",
    )
