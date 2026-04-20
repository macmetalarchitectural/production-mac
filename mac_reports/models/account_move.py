# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_invoice_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    invoice_note_terms = fields.Text('Terms and conditions', default=_default_invoice_note_terms, translate=True, copy=False)

    def information_block_to_display(self):
        blocks = super().information_block_to_display()
        payment_term = {
            'invoice_payment_term_id': {
                'label': _('Payment terms'),
                'value': self.invoice_payment_term_id.name if self.invoice_payment_term_id else False,
                'type': 'string',
            }
        }
        result = {}
        for key, val in blocks.items():
            result[key] = val
            if key == 'invoice_date':
                result.update(payment_term)
        if 'invoice_payment_term_id' not in result:
            result.update(payment_term)
        return result

    def _get_not_termes_from_settings(self):
        self.ensure_one()
        use_company_terms = self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms'
        )
        if use_company_terms:
            return self.env.company.sale_order_terms or ''
        return self.invoice_note_terms or ''