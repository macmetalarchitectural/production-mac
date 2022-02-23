# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.exceptions import UserError


class SaleOrderNote(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_sale_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    delivery_note = fields.Text('Delivery Note')
    sale_note_termes = fields.Text('Terms and conditions', default=_default_sale_note_terms, translate=True)