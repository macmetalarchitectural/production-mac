# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    e3k_drawing = fields.Html(string="Drawing")  # no-check
