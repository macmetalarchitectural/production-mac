# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SaleOrderNote(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_sale_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    delivery_note = fields.Text('Delivery Note')
    sale_note_termes = fields.Text('SO Terms and conditions', default=_default_sale_note_terms, translate=True, copy=False)
    client_order_ref = fields.Text(string='Customer Reference', copy=False)

    def information_block_to_display(self):
        result = super().information_block_to_display()

        result.update({
            'e3k_inside_sales_rep_id': {
                'label': _('Inside sales rep'),
                'value': self.e3k_inside_sales_rep_id.name or False,
                'type': 'string',
            }
        })

        result.pop('property_delivery_carrier_id')

        if self.state == 'sale':
            result.pop('commitment_date')

        return result

    def _get_not_termes_from_settings(self):
        self.ensure_one()
        use_company_terms = self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms'
        )
        if use_company_terms:
            return self.env.company.sale_order_terms or ''
        return self.sale_note_termes or ''