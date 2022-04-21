# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_payment_pick_invoices(models.TransientModel):
    _name = "account.payment.pick.invoices"

    def _default_payment_id(self):
        payment_id = self._context.get('active_model') == 'account.payment' and self._context.get('active_ids') or []
        return payment_id[0]

    def _default_type_invoice(self):
        payment_id = self._context.get('active_model') == 'account.payment' and self._context.get('active_ids') or []
        type_invoice = ''
        if payment_id:
            payment_id_obj = self.env['account.payment'].search([('id','=',payment_id[0])])
            if payment_id_obj.partner_type == 'customer':
                type_invoice = 'out_invoice'
            else:
                type_invoice = 'in_invoice'
        return  type_invoice

    def _default_type_refund(self):
        payment_id = self._context.get('active_model') == 'account.payment' and self._context.get('active_ids') or []
        type_refund = ''
        if payment_id:
            payment_id_obj = self.env['account.payment'].search([('id','=',payment_id[0])])
            if payment_id_obj.partner_type == 'customer':
                type_refund = 'out_refund'
            else:
                type_refund = 'in_refund'
        return  type_refund


    invoice_ids = fields.Many2many('account.move', 'account_payment_pick_invoices_rel', 'pick_id', 'invoice_id',
                                   string="Invoices", copy=False)
    payment_id = fields.Many2one('account.payment', string='Payment', default=_default_payment_id)
    partner_id = fields.Many2one('res.partner', related='payment_id.partner_id', string='Partner', readonly=True)
    str_child_partner_list = fields.Text(related='payment_id.str_child_partner_list', string='Partner Contacts')
    type_invoice = fields.Selection([
            ('in_invoice', 'Fournisseur'),
            ('out_invoice', 'Client'),
        ], string='Type invoices',default=_default_type_invoice)

    type_refund = fields.Selection([
            ('in_refund', 'Avoir Fournisseur'),
            ('out_refund', 'Avoir Client'),
        ], string='Type Refund',default=_default_type_refund)

    rel_child_partner_ids = fields.Many2many('res.partner',related="payment_id.child_partner_ids",
                                         string='Partner Contacts')


    def edit_invoice_ids(self):
        if not self.partner_id:
            return {}
        new_lines = self.env['account.payment.partial']
        if self.invoice_ids:
            used_invoice_ids = self.payment_id.payment_partial_in_ids.mapped('invoice_id').ids
            used_invoice_ids += self.payment_id.payment_partial_ids.mapped('invoice_id').ids
            new_invoice_ids = self.invoice_ids.filtered(lambda inv: inv.id not in used_invoice_ids)
            for line in new_invoice_ids:
                new_line = new_lines.new({
                    'invoice_id': line.id,
                    'currency_id': line.currency_id.id,
                    'payment_id': self.payment_id.id
                })
                new_line.onchange_invoice_id()
                new_lines += new_line

            if self.payment_id.partner_type == 'customer':
                self.payment_id.payment_partial_in_ids += new_lines
                total_to_pay = 0.00
                for line in self.payment_id.payment_partial_in_ids:
                    total_to_pay += line.partial_payment
                self.payment_id.amount = total_to_pay

            if self.payment_id.partner_type == 'supplier':
                self.payment_id.payment_partial_ids += new_lines
                total_to_pay = 0.00
                for line in self.payment_id.payment_partial_ids:
                    total_to_pay += line.partial_payment
                self.payment_id.amount = total_to_pay

        return {'type': 'ir.actions.act_window_close'}
