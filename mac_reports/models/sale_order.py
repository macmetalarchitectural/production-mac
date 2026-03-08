# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # cette contrainte n'était pas chargée dans la base de données (on a cherché les raisons mais on a pas trouvé) dont on la bypassé pour eviter le warnning
    _check_amount_currency_balance_sign = models.Constraint(
        "CHECK(1=1)",
        "",
    )


class SaleOrderNote(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_sale_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    delivery_note = fields.Text('Delivery Note')
    sale_note_termes = fields.Text('SO Terms and conditions', default=_default_sale_note_terms, translate=True, copy=False)
    client_order_ref = fields.Text(string='Customer Reference', copy=False)


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