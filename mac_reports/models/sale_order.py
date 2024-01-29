# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrderNote(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_sale_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    delivery_note = fields.Text('Delivery Note')
    sale_note_termes = fields.Text('Terms and conditions', default=_default_sale_note_terms, translate=True, copy=False)
    client_order_ref = fields.Text(string='Customer Reference', copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        sales = super(SaleOrderNote, self).create(vals_list)
        for res in sales:
            languages = self.env['res.lang'].sudo().search([('active', '=', True)])
            for language in languages:
                translation = [
                    {
                        'type': 'model',
                        'name': 'sale.order,sale_note_termes',
                        'module': 'mac_reports',
                        'res_id': res.id,
                        'src': res.sale_note_termes,
                        'value': res.env.company.sudo().with_context(lang=language.code).sale_order_terms,
                        'lang': language.code,
                    }
                ]
                existing_trans = self.env['ir.translation'].search([('name', '=', 'sale.order,sale_note_termes'),
                                                                    ('res_id', '=', res.id),
                                                                    ('lang', '=', language.code)])
                if not existing_trans:
                    self.env['ir.translation'].sudo().create(translation)

        return sales


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_invoice_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    invoice_note_terms = fields.Text('Terms and conditions', default=_default_invoice_note_terms, translate=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
        for res in moves:
            languages = self.env['res.lang'].sudo().search([('active', '=', True)])
            for language in languages:
                translation = [
                    {
                        'type': 'model',
                        'name': 'account.move,invoice_note_terms',
                        'module': 'mac_reports',
                        'res_id': res.id,
                        'src': res.invoice_note_terms,
                        'value': res.env.company.sudo().with_context(lang=language.code).sale_order_terms,
                        'lang': language.code,
                    }
                ]
                existing_trans = self.env['ir.translation'].search([('name', '=', 'account.move,invoice_note_terms'),
                                                                    ('res_id', '=', res.id),
                                                                    ('lang', '=', language.code)])
                if not existing_trans:
                    self.env['ir.translation'].sudo().create(translation)

        return moves