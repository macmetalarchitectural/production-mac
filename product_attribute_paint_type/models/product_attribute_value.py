# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductAttributeValueWithPaintType(models.Model):

    _inherit = 'product.attribute.value'

    paint_type = fields.Char('Paint Type')
