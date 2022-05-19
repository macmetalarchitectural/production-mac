# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import collections
from odoo.exceptions import ValidationError, UserError
import math
from odoo.tools import float_round
# from odoo.tools.float_utils import float_round
from odoo.tools import float_utils
import json
import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_partial_ids = fields.One2many('account.payment.partial', 'payment_id', string='Payment Lines', copy=True)
    payment_partial_in_ids = fields.One2many('account.payment.partial', 'payment_in_id', string='Payment Lines',
                                             copy=True)
    total_partial_amount = fields.Monetary(string='Payment Amount', store=True, readonly=True,
                                           compute='_compute_payment_amount_total', track_visibility='always')
    difference_amount = fields.Monetary(string='Difference Amount', readonly=True,
                                        compute='_compute_payment_difference_amount', track_visibility='always')
    discount_move_id = fields.Many2one('account.move', string='Discount Entries', store=True, readonly=True)
    child_partner_ids = fields.Many2many('res.partner', 'payment_child_partner_rel', 'payment_id', 'child_partner_id',
                                         string='Partner Contacts')
    str_child_partner_list = fields.Text(string='Partner Contacts')
    notif_partner = fields.Many2one('res.partner', string='Notifie partner', compute='_compute_notif_partner'
                                   )

    partial_writeoff_account_id = fields.Many2one('account.account', string="Difference Account", copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")

    show_write_off = fields.Boolean(string = "Show / hide", compute="compute_display_write_off")

    @api.depends('partial_writeoff_account_id','difference_amount','total_partial_amount')
    def compute_display_write_off(self):
        for rec in self:
            if (rec.partner_type == 'supplier' and rec.difference_amount < 0) or \
                (rec.partner_type == 'customer' and rec.difference_amount > 0)  :
                rec.show_write_off = True
            else:
                rec.show_write_off = False
                rec.partial_writeoff_account_id = False

            for partial in rec.payment_partial_ids and rec.payment_partial_ids:
                if partial.done_discount_amount or partial.invoice_id.move_type in ['in_refund', 'out_refund']:
                    rec.show_write_off = False
                    rec.partial_writeoff_account_id = False





    @api.model_create_multi
    def create(self,vals):
        for val in vals:
            payment_type = val['payment_type']
            if payment_type and payment_type =='inbound':
                val['amount'] = val['amount'] or 1

        return super(AccountPayment, self).create(vals)


    @api.depends('invoice_ids', 'amount', 'date', 'currency_id', 'payment_type', 'payment_partial_ids',
                 'payment_partial_in_ids')
    def _compute_payment_difference(self):
        partial_draft_payments = self.filtered(lambda p: p.payment_partial_ids and p.state == 'draft')
        partial_in_draft_payments = self.filtered(lambda p: p.payment_partial_in_ids and p.state == 'draft')
        if partial_in_draft_payments:
            for pay in partial_in_draft_payments:
                payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount
                total_partial_amount = 0.0
                for line in pay.payment_partial_in_ids:
                    total_partial_amount += line.partial_payment
                pay.payment_difference = total_partial_amount - payment_amount
            (self - partial_in_draft_payments).payment_difference = 0
        elif partial_draft_payments:
            for pay in partial_draft_payments:
                payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount
                payment_amount = -payment_amount
                total_partial_amount = 0.0
                for line in pay.payment_partial_ids:
                    total_partial_amount += line.partial_payment
                pay.payment_difference = payment_amount - total_partial_amount
            (self - partial_draft_payments).payment_difference = 0
        else:
            super(AccountPayment, self)._compute_payment_difference()

    @api.depends('payment_partial_in_ids', 'payment_partial_ids')
    def _compute_payment_amount_total(self):
        for acc in self:
            if acc.state == 'draft':
                if acc.payment_partial_in_ids:
                    acc.total_partial_amount = sum(line.partial_payment for line in acc.payment_partial_in_ids) or 0.0
                    # acc.amount = sum(line.partial_payment for line in acc.payment_partial_in_ids) or 0.0
                    sum_partial_lines = sum(line.partial_payment for line in acc.payment_partial_in_ids) or 0.0
                    if not (round(sum_partial_lines, 2) - acc.difference_amount == round(acc.amount, 2)):
                        acc.amount = sum_partial_lines
                    invoice_ids = []
                    for payment_line in acc.payment_partial_in_ids:
                        invoice_ids.append(payment_line.invoice_id.id)
                        if invoice_ids and [item for item, count in list(collections.Counter(invoice_ids).items()) if
                                            count > 1]:
                            raise ValidationError(_("You can't create many lines with the same invoice"))

                elif acc.payment_partial_ids:
                    acc.total_partial_amount = sum(line.partial_payment for line in acc.payment_partial_ids) or 0.0
                    sum_partial_lines = sum(line.partial_payment for line in acc.payment_partial_ids) or 0.0
                    if not (round(sum_partial_lines, 2) + acc.difference_amount == round(acc.amount, 2)):
                        acc.amount = sum_partial_lines
                    # acc.amount = sum(line.partial_payment for line in acc.payment_partial_ids) or 0.0
                    invoice_ids = []
                    for payment_line in acc.payment_partial_ids:
                        invoice_ids.append(payment_line.invoice_id.id)
                    if invoice_ids and [item for item, count in list(collections.Counter(invoice_ids).items()) if
                                        count > 1]:
                        raise ValidationError(_("You can't create many lines with the same invoice"))
                else:
                    # acc.total_partial_amount = 0.0
                    acc.total_partial_amount = acc.amount
                acc.amount = acc.total_partial_amount


    @api.depends('amount')
    def _compute_payment_difference_amount(self):
        for payment in self:
            if payment.payment_partial_in_ids:
                total_partial_amount = sum(line.partial_payment for line in payment.payment_partial_in_ids)
                payment.difference_amount = -(payment.amount - total_partial_amount)
            elif payment.payment_partial_ids:
                total_partial_amount = sum(line.partial_payment for line in payment.payment_partial_ids)
                payment.difference_amount = (payment.amount - total_partial_amount)
            else:
                payment.difference_amount = 0.0

            # if payment.amount:
            #     # remplacer lang=payment.partner_id.lang or 'en' ##
            #     check_amount_in_words = payment.currency_id.with_context(
            #         lang=payment.partner_id.lang or 'es_ES').amount_to_text(
            #         math.floor(payment.amount))
            #
            #     check_amount_in_words = check_amount_in_words.replace(' and Zero Cent', '')  # Ugh
            #     decimals = payment.amount % 1
            #     if decimals >= 10 ** -2:
            #         check_amount_in_words += _(' and %s/100') % str(
            #             int(round(float_round(decimals * 100, precision_rounding=1))))
            #     payment.check_amount_in_words = check_amount_in_words
            # else:
            #     payment.check_amount_in_words = 'Zero'

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        partner_domain = [('is_company', '=', True)]
        if self.partner_type == 'customer':
            partner_domain.append(('customer_rank', '>', 0))
        # elif self.partner_type == 'supplier':
        else:
            partner_domain.append(('supplier_rank', '>', 0))
        return {'domain': {'domain': {'partner_id': partner_domain}}}

    def cancel(self):
        for rec in self:
            for move in rec.move_id.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            rec.state = 'draft'
            rec.move_name = False
            rec.write({'invoice_ids': [[6, False, []]]})



    def get_payment_notification_message_view(self):
        self.ensure_one()
        template = self.env.ref('e3k_advanced_payment.email_template_payment_notification', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.payment',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            default_reply_to=self.env.user.email or ''
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'reports': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def cancel_void(self):
        self.write({'state': 'cancel'})

    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        res = {}
        for payment_id in res_ids:
            res[payment_id] = self.env.user.email or ''
        return res

    @api.onchange('partner_id')
    def _onchange_get_partner_childs_id(self):
        if not self.partner_id:
            return {}

        if self.partner_id:
            contact_ids = [self.partner_id.id]
            for contact in self.partner_id.child_ids:
                contact_ids.append(contact.id)
            self.child_partner_ids = [(6, 0, contact_ids)]
            self.str_child_partner_list = str(contact_ids)

    def _check_partial_amount(self):
        for payment in self:
            for line in payment.payment_partial_ids:
                new_residual_signed = line.invoice_id.currency_id._convert(line.amount_residual_signed,
                                                                           line.payment_id.currency_id,
                                                                           line.payment_id.company_id,
                                                                           line.payment_id.date)

                if abs(line.partial_payment + line.done_discount_amount) - abs(new_residual_signed) > 0.001:
                    raise ValidationError(
                        'Invoice [' + line.invoice_id.name + '], (Partial payment + Discount) must be less or equal to To-Pay : ' + str(
                            new_residual_signed) + ' ' + payment.currency_id.name + '.')
                    return False

        return True

    def _check_partial_amount_positif(self):
        for payment in self:
            for line in payment.payment_partial_ids:
                if line.partial_payment <= 0:
                    return False
        return True

    _constraints = [
        (_check_partial_amount, "The Partial payments must be <= To Pay", ["payment_partial_ids"]),
    ]

    def delete_invoice_ids(self):
        for payment in self:
            payment.invoice_ids = [[6, False, []]]

    def _prepare_and_post_discount_payment_moves(self):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)

        sum_discount_debit = 0.00
        sum_discount_credit = 0.00
        sum_discount = 0.0
        journal_before_id = None
        discount_move = None

        # customer payment *************************************
        if self.payment_partial_in_ids:
            for partial_line in self.payment_partial_in_ids:
                if partial_line.done_discount_amount:
                    discount_move_value = {
                        'date': self.date,
                        'ref': self.ref,
                        'journal_id': self.journal_id.id,
                        'currency_id': self.currency_id.id or self.company_id.currency_id.id,
                        'partner_id': self.partner_id.id,
                    }
                    if self.payment_type == 'inbound':
                        customer_journal_id = self.env['account.journal.discount'].search(
                            [('company_id', '=', self.company_id.id)]) or None
                        if customer_journal_id and customer_journal_id.journal_discount_client_id:
                            customer_journal_id = customer_journal_id.journal_discount_client_id.id
                            discount_move_value['journal_id'] = customer_journal_id

                    elif self.payment_type == 'outbound':
                        vendor_journal_id = self.env['account.journal.discount'].search(
                            [('company_id', '=', self.company_id.id)]) or None

                        if vendor_journal_id and vendor_journal_id.journal_discount_supplier_id:
                            vendor_journal_id = vendor_journal_id.journal_discount_supplier_id.id
                            discount_move_value['journal_id'] = vendor_journal_id

                    discount_move = self.env['account.move'].create(discount_move_value)
                    break

            if discount_move:
                self.write({'discount_move_id': discount_move.id})
                journal_before_id = discount_move.journal_id.id

        # supplier payment *************************************
        if self.payment_partial_ids and (self.payment_type == 'outbound'):
            for partial_line in self.payment_partial_ids:
                if partial_line.done_discount_amount:
                    discount_move_value = {
                        'date': self.date,
                        'ref': self.ref,
                        'journal_id': self.journal_id.id,
                        'currency_id': self.currency_id.id or self.company_id.currency_id.id,
                        'partner_id': self.partner_id.id,
                    }

                    if self.payment_type == 'outbound':
                        vendor_journal_id = self.env['account.journal.discount'].search(
                            [('company_id', '=', self.company_id.id)]) or None

                        if vendor_journal_id and vendor_journal_id.journal_discount_supplier_id:
                            vendor_journal_id = vendor_journal_id.journal_discount_supplier_id.id
                            discount_move_value['journal_id'] = vendor_journal_id

                    discount_move = self.env['account.move'].create(discount_move_value)

                    break

            if discount_move:
                self.write({'discount_move_id': discount_move.id})
                journal_before_id = discount_move.journal_id.id

        if self.payment_partial_ids:
            i = 0
            for partial in self.payment_partial_ids:
                if self.payment_partial_in_ids and partial.done_discount_amount:
                    client_payment_discount_account_id = None
                    if partial.invoice_id and partial.invoice_id.invoice_payment_term_id and partial.invoice_id.invoice_payment_term_id.payment_term_discount_ids:
                        for line_discount_account in partial.invoice_id.invoice_payment_term_id.payment_term_discount_ids:
                            if line_discount_account.company_id.id == self.company_id.id:
                                client_payment_discount_account_id = line_discount_account.payment_discount_account.id
                    else:
                        all_account_discount = self.env['account.journal.discount'].search([])
                        default_account_discount = all_account_discount.\
                            filtered(lambda r: r.company_id == partial.invoice_id.company_id and r.journal_discount_client_id.default_account_id)
                        if len(default_account_discount)>0:
                            client_payment_discount_account_id = default_account_discount[0].journal_discount_client_id.default_account_id.id

                    if not client_payment_discount_account_id:
                        raise ValidationError(_(
                            "You need to set an discount account for the payment term related to the invoice : " + partial.invoice_id.name + "\n and the company: " + self.company_id.name))
                    company_currency = partial.payment_id.company_id.currency_id
                    done_discount_amount = partial.done_discount_amount
                    if partial.payment_id.currency_id != company_currency:
                        done_discount_amount = partial.payment_id.currency_id._convert(partial.done_discount_amount,
                                                                                       company_currency,
                                                                                       partial.payment_id.company_id,
                                                                                       partial.payment_id.date)

                    credit = done_discount_amount > 0.0 and done_discount_amount or 0.0
                    debit = done_discount_amount < 0.0 and done_discount_amount or 0.0
                    sum_discount_debit += debit
                    sum_discount_credit += credit
                    sum_discount += partial.done_discount_amount
                    # conterpart_partial_discount_amount
                    if partial.payment_id.payment_type in ('outbound', 'transfer'):
                        conterpart_partial_discount_amount = partial.done_discount_amount
                    else:
                        conterpart_partial_discount_amount = -partial.done_discount_amount

                    # currency_id
                    if partial.payment_id.currency_id == company_currency:
                        currency_id = False
                    else:
                        currency_id = partial.payment_id.currency_id.id

                    # Manage custom currency on journal for liquidity line.
                    if partial.payment_id.journal_id.currency_id and partial.payment_id.currency_id != partial_line.payment_id.journal_id.currency_id:
                        # Custom currency on journal.
                        if partial.payment_id.journal_id.currency_id == company_currency:
                            # Single-currency
                            liquidity_line_currency_id = False
                        else:
                            liquidity_line_currency_id = partial.payment_id.journal_id.currency_id.id
                        liquidity_amount = company_currency._convert(
                            done_discount_amount,
                            partial.payment_id.journal_id.currency_id,
                            partial.payment_id.company_id,
                            partial.payment_id.date)
                    else:
                        # Use the payment currency.
                        liquidity_line_currency_id = currency_id
                        liquidity_amount = conterpart_partial_discount_amount

                    if  partial.invoice_id.move_type  in ['in_refund','out_refund'] :
                        new_debit = credit
                        new_credit = debit
                        credit = new_credit
                        debit = new_debit

                    if discount_move:
                        counterpart_aml_dict = {
                            'amount_currency': -partial.done_discount_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'name': 'Discount invoice: ' + partial.invoice_id.name,
                            'credit': credit,
                            'debit': debit,
                            'date_maturity': self.date,
                            'partner_id': self.partner_id.id,
                            'account_id': self.destination_account_id.id,
                            'payment_id': self.id,
                            'payment_invoice_id': partial.invoice_id.id,
                            'partial_payment_line_id': partial.id,
                            'move_id': discount_move.id,
                        }

                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                    debit = done_discount_amount > 0.0 and done_discount_amount or 0.0
                    credit = done_discount_amount < 0.0 and -done_discount_amount or 0.0
                    amount_currency_liquidity_amount = 0.0
                    if debit:
                        amount_currency_liquidity_amount = abs(liquidity_amount)
                    if credit:
                        amount_currency_liquidity_amount = - abs(liquidity_amount)

                    if  partial.invoice_id.move_type  in ['in_refund','out_refund'] :
                        new_debit = credit
                        new_credit = debit
                        credit = new_credit
                        debit = new_debit

                    liquidity_aml_dict = {
                        'amount_currency': amount_currency_liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'name': 'Discount invoice : ' + partial.invoice_id.name,
                        'credit': credit,
                        'debit': debit,
                        'date_maturity': self.date,
                        'partner_id': self.partner_id.id,
                        'account_id': client_payment_discount_account_id,
                        'payment_id': self.id,
                        'move_id': discount_move.id,
                    }

                    aml_obj.create(liquidity_aml_dict)

                if self.payment_partial_ids and (self.payment_type == 'outbound') and partial.done_discount_amount:
                    payment_supplier_discount_account = None
                    if partial.invoice_id and partial.invoice_id.invoice_payment_term_id and partial.invoice_id.invoice_payment_term_id.payment_term_discount_ids:
                        for line_discount_account in partial.invoice_id.invoice_payment_term_id.payment_term_discount_ids:
                            if line_discount_account.company_id.id == self.company_id.id:
                                payment_supplier_discount_account = line_discount_account.payment_supplier_discount_account.id

                    else:
                        all_account_discount = self.env['account.journal.discount'].search([])
                        default_account_discount_supp = all_account_discount. \
                            filtered(lambda r: r.company_id == partial.invoice_id.company_id and r.journal_discount_supplier_id.default_account_id)
                        if len(default_account_discount_supp)>0:
                            payment_supplier_discount_account = default_account_discount_supp[0].journal_discount_supplier_id.default_account_id.id

                    if not payment_supplier_discount_account:
                        raise ValidationError(_(
                            "You need to set an discount account for the payment term related to the invoice : " + partial.invoice_id.name + "\n and the company: " + self.company_id.name))

                    company_currency = partial.payment_id.company_id.currency_id
                    done_discount_amount = partial.done_discount_amount
                    if partial.payment_id.currency_id != company_currency:
                        done_discount_amount = partial.payment_id.currency_id._convert(partial.done_discount_amount,
                                                                                       company_currency,
                                                                                       partial.payment_id.company_id,
                                                                                       partial.payment_id.date)

                    debit = done_discount_amount > 0.0 and done_discount_amount or 0.0
                    credit = done_discount_amount < 0.0 and done_discount_amount or 0.0
                    sum_discount_debit += debit
                    sum_discount_credit += credit
                    sum_discount += partial.done_discount_amount

                    # conterpart_partial_discount_amount
                    if partial.payment_id.payment_type in ('outbound', 'transfer'):
                        conterpart_partial_discount_amount = partial.done_discount_amount
                    else:
                        conterpart_partial_discount_amount = -partial.done_discount_amount

                    # currency_id
                    if partial.payment_id.currency_id == company_currency:
                        currency_id = False
                    else:
                        currency_id = partial.payment_id.currency_id.id

                    # Manage custom currency on journal for liquidity line.
                    if partial.payment_id.journal_id.currency_id and partial.payment_id.currency_id != partial_line.payment_id.journal_id.currency_id:
                        # Custom currency on journal.
                        if partial.payment_id.journal_id.currency_id == company_currency:
                            # Single-currency
                            liquidity_line_currency_id = False
                        else:
                            liquidity_line_currency_id = partial.payment_id.journal_id.currency_id.id
                        liquidity_amount = company_currency._convert(
                            done_discount_amount,
                            partial.payment_id.journal_id.currency_id,
                            partial.payment_id.company_id,
                            partial.payment_id.date)
                    else:
                        # Use the payment currency.
                        liquidity_line_currency_id = currency_id
                        liquidity_amount = conterpart_partial_discount_amount

                    if  partial.invoice_id.move_type  in ['in_refund','out_refund'] :
                        new_debit = credit
                        new_credit = debit
                        credit = new_credit
                        debit = new_debit

                    if discount_move:
                        counterpart_aml_dict = {
                            'amount_currency': partial.done_discount_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'name': 'Discount invoice : ' + partial.invoice_id.name,
                            'credit': credit,
                            'debit': debit,
                            'date_maturity': self.date,
                            'partner_id': self.partner_id.id,
                            'account_id': self.destination_account_id.id,
                            'payment_id': self.id,
                            'payment_invoice_id': partial.invoice_id.id,
                            'partial_payment_line_id': partial.id,
                            'move_id': discount_move.id,
                        }

                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                    credit = done_discount_amount > 0.0 and done_discount_amount or 0.0
                    debit = done_discount_amount < 0.0 and -done_discount_amount or 0.0
                    amount_currency_liquidity_amount = 0.0
                    if debit:
                        amount_currency_liquidity_amount = abs(liquidity_amount)
                    if credit:
                        amount_currency_liquidity_amount = - abs(liquidity_amount)

                    if  partial.invoice_id.move_type  in ['in_refund','out_refund'] :
                        new_debit = credit
                        new_credit = debit
                        credit = new_credit
                        debit = new_debit

                    liquidity_aml_dict = {
                        'amount_currency': amount_currency_liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'name': 'Discount invoice : ' + partial.invoice_id.name,
                        'credit': credit,
                        'debit': debit,
                        'date_maturity': self.date,
                        'partner_id': self.partner_id.id,
                        'account_id': payment_supplier_discount_account,
                        'payment_id': self.id,
                        'move_id': discount_move.id,
                    }

                    aml_obj.create(liquidity_aml_dict)

        if discount_move and journal_before_id:
            discount_move.write({'journal_id': journal_before_id})

        return False


    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_stat_buttons_from_reconciliation(self):
        super(AccountPayment, self)._compute_stat_buttons_from_reconciliation()

        if self.payment_partial_ids:
            invoices = []
            for payment_line in self.payment_partial_ids:
                invoices.append(payment_line.invoice_id.id)
                self.reconciled_invoice_ids =[(6, 0, invoices)]


    def pay_totality(self):
        if self.partial_writeoff_account_id:
            self.move_id.line_ids.unlink()
            write_off_line_vals = {
                'name': 'test',
                'amount': abs(self.difference_amount),
                'account_id': self.partial_writeoff_account_id.id,
            }
            to_write = {'payment_id': self._origin.id}
            to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                    self._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]
            self.move_id.write(to_write)
            self.action_post()

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        self.move_id.line_ids.unlink()
        self.partial_writeoff_account_id = False
        to_write = {'payment_id': self._origin.id}
        to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
                                self._prepare_move_line_default_vals(write_off_line_vals=None)]
        self.move_id.write(to_write)
        if self.discount_move_id:
            for partial in self.payment_partial_ids.mapped('invoice_id'):
                invoice_payments_widget_teste = json.loads(partial.invoice_payments_widget)
                if invoice_payments_widget_teste:
                    for rec in invoice_payments_widget_teste['content']:
                        if rec['move_id'] == self.discount_move_id.id:
                            partial.js_remove_outstanding_partial(rec['partial_id'])
            self.discount_move_id.button_draft()

        for partial in self.payment_partial_ids.mapped('invoice_id'):
            if partial.move_type in ['in_refund', 'out_refund']:
                invoice_payments_widget_teste = json.loads(partial.invoice_payments_widget)
                if invoice_payments_widget_teste:
                    for rec in invoice_payments_widget_teste['content']:
                        if rec['move_id'] in self.payment_partial_ids.mapped('invoice_id').ids:
                            partial.js_remove_outstanding_partial(rec['partial_id'])



    def action_post(self):
        res = super(AccountPayment, self).action_post()
        journal_name = []
        for rec in self:
            if not rec.discount_move_id:
                rec._prepare_and_post_discount_payment_moves()
            rec.process_payment()

    def process_payment(self):
        if self.discount_move_id:
            self.discount_move_id._post(soft=False)
        if self.payment_partial_ids:
            exit_bc = True
            filter_liste = []
            invoices_ids = self.payment_partial_ids.mapped('invoice_id').filtered(lambda r: r.move_type not in ['in_refund', 'out_refund']).ids
            reconciled = []
            for partial_payment in self.payment_partial_ids:
                # if partial_payment.invoice_id.move_type not in ['in_refund', 'out_refund']:
                if self.discount_move_id:
                    to_reconcile_payments_widget_vals = json.loads(
                        partial_payment.invoice_id.invoice_outstanding_credits_debits_widget)
                    print('to_reconcile_payments_widget_vals',to_reconcile_payments_widget_vals)

                    if to_reconcile_payments_widget_vals:

                        check_move = [self.discount_move_id.id,self.move_id.id]
                        print('check_move',check_move)
                        current_amounts = {}
                        for vals in to_reconcile_payments_widget_vals['content']:
                            if vals['move_id'] == self.discount_move_id.id:# check_move: #and vals['move_id'] :##not in filter_liste:
                                print('vals', vals)
                                move_line = self.env['account.move.line'].search([('id','=',vals['id'])])
                                if move_line:
                                    if partial_payment.invoice_id.name in move_line[0].name:
                                        print('vals new', vals)
                                        if not move_line.reconciled:
                                            partial_payment.invoice_id.js_assign_outstanding_line(move_line.id)

                            #         current_amounts.update({vals['move_id']: vals['amount']})
                            # print('current_amounts',current_amounts)
                            #
                            # pay_term_lines = partial_payment.invoice_id.line_ids \
                            #     .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                            # to_reconcile = self.env['account.move'].browse(list(current_amounts.keys())) \
                            #     .line_ids \
                            #     .filtered(lambda line: line.account_id == pay_term_lines.account_id)
                            # for line in to_reconcile:
                            #     #if line not in self.move_id.line_ids:
                            #     if not line.reconciled:
                            #         partial_payment.invoice_id.js_assign_outstanding_line(line.id)

            for partial_payment in self.payment_partial_ids:
                if partial_payment.invoice_id.move_type  in ['in_refund', 'out_refund']:
                    to_reconcile_payments_widget_vals = json.loads(
                        partial_payment.invoice_id.invoice_outstanding_credits_debits_widget)

                    current_amounts = {}
                    if to_reconcile_payments_widget_vals:
                        for vals in to_reconcile_payments_widget_vals['content']:
                            if vals['move_id'] in invoices_ids :#and vals['move_id']  :#not in reconciled:
                                #reconciled.append(vals['move_id'])
                                current_amounts.update({vals['move_id']: vals['amount']})
                        teste = self.env['account.move'].browse(list(current_amounts.keys()))
                        pay_term_lines = partial_payment.invoice_id.line_ids\
                                 .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        to_reconcile  =teste.line_ids.filtered(lambda line: line.account_id == pay_term_lines.account_id)
                        for line in to_reconcile:
                            if  partial_payment.invoice_id.amount_residual != 0:
                                if not line.reconciled:
                                    partial_payment.invoice_id.js_assign_outstanding_line(line.id)

            for partial_payment in self.payment_partial_ids:
                if partial_payment.invoice_id.move_type  not in ['in_refund', 'out_refund']:
                    to_reconcile_payments_widget_vals = json.loads(
                        partial_payment.invoice_id.invoice_outstanding_credits_debits_widget)
                    #partial_payment.invoice_id._compute_payments_widget_reconciled_info()
                    if to_reconcile_payments_widget_vals:
                        current_amounts = {}
                        for vals in to_reconcile_payments_widget_vals['content']:
                            if vals['move_id'] == self.move_id.id:
                                current_amounts.update({vals['move_id']: vals['amount']})
                        teste = self.env['account.move'].browse(list(current_amounts.keys()))
                        pay_term_lines = partial_payment.invoice_id.line_ids\
                                 .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                        to_reconcile  = teste.line_ids.filtered(lambda line: line.account_id == pay_term_lines.account_id)
                        for line in to_reconcile:
                            if not line.reconciled:
                                partial_payment.invoice_id.js_assign_outstanding_line(line.id)
                    else:
                        to_reconcile = [
                            partial_payment.invoice_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))]
                        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
                        payments = self
                        for payment, lines in zip(payments, to_reconcile):
                            payment_lines = payment.line_ids.filtered_domain(domain)
                            for account in payment_lines.account_id:
                                rec1 = payment_lines + lines
                                (payment_lines + lines) \
                                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
                                    .reconcile()



            # for partial_payment in self.payment_partial_ids:
            #     if partial_payment.invoice_id.move_type  in ['in_refund', 'out_refund']:
            #         to_reconcile_payments_widget_vals = json.loads(
            #             partial_payment.invoice_id.invoice_outstanding_credits_debits_widget)
            #
            #         current_amounts = {}
            #         if to_reconcile_payments_widget_vals:
            #             for vals in to_reconcile_payments_widget_vals['content']:
            #                 if vals['move_id'] in invoices_ids :#and vals['move_id']  :#not in reconciled:
            #                     #reconciled.append(vals['move_id'])
            #                     current_amounts.update({vals['move_id']: vals['amount']})
            #             teste = self.env['account.move'].browse(list(current_amounts.keys()))
            #             pay_term_lines = partial_payment.invoice_id.line_ids\
            #                      .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            #             to_reconcile  =teste.line_ids.filtered(lambda line: line.account_id == pay_term_lines.account_id)
            #             for line in to_reconcile:
            #                 if  partial_payment.invoice_id.amount_residual != 0:
            #                     if not line.reconciled:
            #                         partial_payment.invoice_id.js_assign_outstanding_line(line.id)
            #
            # for partial_payment in self.payment_partial_ids:
            #     if partial_payment.invoice_id.move_type  not in ['in_refund', 'out_refund']:
            #         to_reconcile_payments_widget_vals = json.loads(
            #             partial_payment.invoice_id.invoice_outstanding_credits_debits_widget)
            #         #partial_payment.invoice_id._compute_payments_widget_reconciled_info()
            #         if to_reconcile_payments_widget_vals:
            #             current_amounts = {}
            #             for vals in to_reconcile_payments_widget_vals['content']:
            #                 if vals['move_id'] == self.move_id.id:
            #                     current_amounts.update({vals['move_id']: vals['amount']})
            #             teste = self.env['account.move'].browse(list(current_amounts.keys()))
            #             pay_term_lines = partial_payment.invoice_id.line_ids\
            #                      .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            #             to_reconcile  = teste.line_ids.filtered(lambda line: line.account_id == pay_term_lines.account_id)
            #             for line in to_reconcile:
            #                 if not line.reconciled:
            #                     partial_payment.invoice_id.js_assign_outstanding_line(line.id)
            #         else:
            #             to_reconcile = [
            #                 partial_payment.invoice_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))]
            #             domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
            #             payments = self
            #             for payment, lines in zip(payments, to_reconcile):
            #                 payment_lines = payment.line_ids.filtered_domain(domain)
            #                 for account in payment_lines.account_id:
            #                     rec1 = payment_lines + lines
            #                     (payment_lines + lines) \
            #                         .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
            #                         .reconcile()


            # for partial_payment in self.payment_partial_ids:
            #     if partial_payment.invoice_id.move_type not in ['in_refund', 'out_refund']:
            #         to_reconcile = [
            #             partial_payment.invoice_id.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))]
            #         domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
            #         payments = self
            #         for payment, lines in zip(payments, to_reconcile):
            #             payment_lines = payment.line_ids.filtered_domain(domain)
            #             for account in payment_lines.account_id:
            #                 rec1 = payment_lines + lines
            #                 (payment_lines + lines) \
            #                     .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
            #                     .reconcile()



            # for move in self.payment_partial_ids.mapped('invoice_id'):
            #     if move.move_type not in ['in_refund','out_refund']:
            #         number_of_refund = self.payment_partial_ids.mapped('invoice_id')\
            #             .filtered(lambda r: r.move_type in ['in_refund','out_refund']).ids
            #         if len(number_of_refund)>0:
            #             to_reconcile_payments_widget_vals = json.loads(
            #                 move.invoice_outstanding_credits_debits_widget)
            #             if to_reconcile_payments_widget_vals:
            #                 current_amounts = {}
            #                 for vals in to_reconcile_payments_widget_vals['content']:
            #                     if vals['move_id'] in number_of_refund:
            #                         current_amounts.update({vals['move_id']: vals['amount']})
            #                 pay_term_lines = move.line_ids\
            #                          .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            #                 teste = self.env['account.move'].browse(list(current_amounts.keys()))
            #                 to_reconcile  =teste.line_ids.filtered(lambda line: line.account_id == pay_term_lines.account_id)
            #
            #                 for line in to_reconcile:
            #                     if line not in self.move_id.line_ids:
            #                         move.js_assign_outstanding_line(line.id)



    def _compute_notif_partner(self):
        for payment in self:
            if payment.partner_type == 'supplier':
                if not payment.partner_id.child_ids:
                    payment.notif_partner = payment.partner_id.id
                else:
                    for contact in payment.partner_id.child_ids:
                        if contact.type == 'invoice':
                            payment.notif_partner = contact.id
                            break
                        else:
                            payment.notif_partner = payment.partner_id.id
            else:
                payment.notif_partner = payment.partner_id.id

    @api.constrains('amount')
    def _check_amount(self):
        for payment in self:
            if not payment.amount >= 0.0:
                pass
                raise ValidationError('The payment amount must be strictly positive.')

    def correct_partial_link_invoice(self):
        for line in self.payment_partial_in_ids:
            _logger.warn('\n\n number -----> %s \n\n',line.number)
            invoice = self.env['account.move'].search([('name','=',line.number)],limit=1)
            _logger.warn('\n\n fake invoice -----> %s \n\n',line.invoice_id)
            _logger.warn('\n\n real invoice -----> %s \n\n',invoice)
            if line.invoice_id != invoice and invoice:
                line.invoice_id = invoice