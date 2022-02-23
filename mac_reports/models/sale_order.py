# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.exceptions import UserError


class SaleOrderNote(models.Model):
    _inherit = 'sale.order'

    delivery_note = fields.Text('Delivery Note')
    sale_note_termes = fields.Text('Terms and conditions', default=_default_sale_note_terms, translate=True)