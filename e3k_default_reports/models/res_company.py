# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    b_logo = fields.Binary(string="Becorp Logo", readonly=False)  # no-check
    sale_order_terms = fields.Text(string='Default Sale Terms and Conditions', translate=True)  # no-check
