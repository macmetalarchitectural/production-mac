# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class account_payment_partial(models.Model):
    _name = "account.payment.partial"
    _description = "Partial Payments"
    _order = 'payment_id desc'

    payment_id = fields.Many2one('account.payment', string="Payment")
    payment_in_id = fields.Many2one('account.payment', string="Payment")
    invoice_id = fields.Many2one('account.move', string="Invoice", required=True)
    partial_payment = fields.Float(string='Net', required=True)
    invoice_date = fields.Date(related='invoice_id.invoice_date', string='Invoice Date', readonly=True)
    date_discount = fields.Date(related='invoice_id.date_discount', string='Discount Date', readonly=True)
    number = fields.Char(related='invoice_id.name', store=True, readonly=True, copy=False)
    ref = fields.Char(related='invoice_id.ref', string='Vendor Reference', readonly=True)
    invoice_date_due = fields.Date(related='invoice_id.invoice_date_due', string='Due Date', readonly=True, copy=False)
    invoice_origin = fields.Char(related='invoice_id.invoice_origin', string='Source Document', readonly=True)
    amount_total_signed = fields.Monetary(related='invoice_id.amount_total_signed', string='Total', store=True,
                                          readonly=True)
    amount_residual_signed = fields.Monetary(related='invoice_id.amount_residual_signed', string='Amount Due',
                                             store=True)
    amount_total = fields.Monetary(string='Total', store=True,
                                   readonly=True,
                                   compute="get_amount_total_residual")  # ,related='invoice_id.amount_total')

    amount_residual = fields.Monetary(string='Amount Due',
                                      store=True,
                                      compute="get_amount_total_residual")  # ,related='invoice_id.amount_residual')

    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_discount_amount = fields.Monetary(related='invoice_id.payment_discount_amount', string='Discount Amount',
                                              store=True)
    due_payment_discount_amount = fields.Monetary(related='invoice_id.due_payment_discount_amount',
                                                  string='Due Discount Amount', store=True)
    done_discount_amount_invisible = fields.Monetary(string='Discount invisible')
    done_discount_amount = fields.Monetary(string='Discount')
    done_discount_amount_in_out_refund = fields.Monetary(string='Discount')

    done_discount_amount_signed = fields.Monetary(string='Discount', compute='_get_done_discount_amount_signed')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], related='invoice_id.payment_state', string='Status', index=True, readonly=True, default='draft')
    acc_move_line_ids = fields.One2many('account.move.line', 'partial_payment_line_id', string='Move lines', copy=False)

    @api.depends('done_discount_amount')
    def get_amount_total_residual(self):
        for partial in self:
            if partial.invoice_id.move_type in ['out_refund','in_refund']:
                partial.amount_total = - partial.invoice_id.amount_residual
                partial.amount_residual = - partial.invoice_id.amount_residual
            else:
                partial.amount_total = partial.invoice_id.amount_residual
                partial.amount_residual = partial.invoice_id.amount_residual

    def _get_done_discount_amount_signed(self):
        for partial in self:
            discount = 0.0
            if partial.payment_id.currency_id.id != partial.payment_id.company_id.currency_id.id:
                partial.done_discount_amount_signed = partial.payment_id.currency_id._convert(
                    partial.done_discount_amount,
                    partial.payment_id.company_id.currency_id,
                    partial.payment_id.company_id,
                    partial.payment_id.date)

            else:
                partial.done_discount_amount_signed = partial.done_discount_amount

    def _get_done_discount_amount(self):
        for partial in self:
            if partial.invoice_id and partial.payment_in_id:
                invoice_brw = self.env['account.move'].browse(partial.invoice_id)
                payment_currency = self.env['res.currency'].browse(partial.payment_in_id.currency_id.id)
                due_payment_discount_amount = invoice_brw.due_payment_discount_amount

                if partial.payment_id.date > partial.date_discount:
                    self.done_discount_amount = 0


                elif invoice_brw.company_id.currency_id.id != partial.payment_id.company_id.currency_id.id:
                    self.done_discount_amount = invoice_brw.company_id.currency_id._convert(due_payment_discount_amount,
                                                                                            payment_currency,
                                                                                            self.payment_id.company_id,
                                                                                            self.payment_id.date)
                else:
                    self.done_discount_amount = due_payment_discount_amount

    # TODO: To improved
    # to add  partial_payment field compute and store and implements in the compte methode the logique of onchange.
    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if self.invoice_id:
            payment_id = self.payment_id or self.payment_in_id
            payment_currency = payment_id.currency_id
            payment_date = payment_id.date

            amount_residual = self.invoice_id.amount_residual

            partial_payment = self.invoice_id.currency_id._convert(
                amount_residual,
                payment_currency,
                self.payment_id.company_id,
                payment_date)

            due_payment_discount_amount = self.invoice_id.due_payment_discount_amount

            product_excluded_discount = self.invoice_id.invoice_line_ids.filtered(
                lambda r: r.product_id.categ_id in self.invoice_id.invoice_payment_term_id.product_category_ids
                          and self.invoice_id.invoice_payment_term_id.product_category_ids)

            if self.invoice_id.company_id.currency_id.id != payment_currency.id:
                due_discount_amount = self.invoice_id.company_id.currency_id._convert(due_payment_discount_amount,
                                                                                      payment_currency,
                                                                                      self.payment_id.company_id,
                                                                                      payment_date)
            else:
                due_discount_amount = due_payment_discount_amount

            if payment_date > self.invoice_id.date_discount or len(product_excluded_discount) > 0:
                due_discount_amount = 0
                partial_payment += due_discount_amount


            self.partial_payment = partial_payment

            # self.done_discount_amount_in_out_refund = -due_discount_amount


            if self.invoice_id.move_type in ['in_refund','out_refund']:
                self.done_discount_amount = abs(due_discount_amount)
                self.partial_payment = -(abs(self.partial_payment) - abs(due_discount_amount))
                self.done_discount_amount_in_out_refund = - abs(due_discount_amount)
            else:
                self.done_discount_amount = abs(due_discount_amount)
                self.partial_payment = abs(self.partial_payment) - abs(self.done_discount_amount)
                self.done_discount_amount_in_out_refund = abs(due_discount_amount)


            # if self.invoice_id.move_type == 'out_refund':
            #     partial_payment = partial_payment + due_discount_amount
            # if self.invoice_id.move_type == 'in_refund':
            #     partial_payment = partial_payment - due_discount_amount
            # if self.invoice_id.move_type == 'in_invoice':
            #     partial_payment = self.invoice_id.amount_residual + due_discount_amount
            # if self.invoice_id.move_type == 'out_invoice':
            #     partial_payment = self.invoice_id.amount_residual - due_discount_amount
            # self.partial_payment = partial_payment
            #
            # if self.invoice_id.move_type == 'in_invoice':
            #     self.done_discount_amount = -due_discount_amount
            # if self.invoice_id.move_type == ('out_invoice'):
            #     self.done_discount_amount = due_discount_amount
            # if self.invoice_id.move_type == 'out_refund':
            #     self.partial_payment = -partial_payment
            #     self.done_discount_amount = -due_discount_amount
            # if self.invoice_id.move_type == 'in_refund':
            #     self.partial_payment = -partial_payment
            #     self.done_discount_amount = due_discount_amount
            # self.get_amount_total_residual()

    @api.onchange('done_discount_amount')
    def onchange_done_discount_amount(self):
        if self.invoice_id:
            payment_id = self.payment_id or self.payment_in_id
            payment_currency = payment_id.currency_id
            payment_date = payment_id.date

            amount_residual = self.invoice_id.amount_residual
            partial_payment = self.invoice_id.currency_id._convert(amount_residual, payment_currency,
                                                                   self.payment_id.company_id, payment_date)

            partial_payment = partial_payment - self.done_discount_amount
            self.partial_payment = partial_payment
            if self.invoice_id.move_type in ['in_refund','out_refund']:
                self.partial_payment = -self.partial_payment

    @api.onchange('done_discount_amount_in_out_refund')
    def onchange_done_discount_amount_in_out_refund(self):
        if self.invoice_id.move_type in ['in_refund','out_refund']:
            if self.done_discount_amount_in_out_refund > 0.0:
                raise ValidationError("the discount in refund must be negative")
        else:
            if self.done_discount_amount_in_out_refund < 0.0:
                raise ValidationError("the discount in invoice must be Positive")
        self.done_discount_amount = abs(self.done_discount_amount_in_out_refund)
        self.onchange_done_discount_amount()

    @api.onchange('partial_payment')
    def onchange_partial_payment(self):
        if self.invoice_id:
            payment_id = self.payment_id or self.payment_in_id
            payment_currency = payment_id.currency_id
            payment_date = payment_id.date
            partial_payment = self.partial_payment

            # amount_residual_signed = self.invoice_id.amount_residual_signed
            amount_residual_signed = self.invoice_id.amount_residual_signed
            total_partial_payment = self.invoice_id.currency_id._convert(amount_residual_signed, payment_currency,
                                                                         self.payment_id.company_id, payment_date)
            # print('amount_residual_signed', amount_residual_signed)
            # print('total_partial_payment',total_partial_payment)
            # print('partial_payment', partial_payment)
            # print('self.done_discount_amount', self.done_discount_amount)
            # if payment_id.partner_type == "customer":
            #     if total_partial_payment - (partial_payment + self.done_discount_amount) < -0.001:
            #         str_error = 'Invoice [{number}] , (Partial payment + Discount) ' \
            #                     'must be less or equal to To-Pay : {total_partial_payment} {name}.'
            #         raise ValidationError(str_error.format(
            #             number=self.invoice_id.name,
            #             total_partial_payment=total_partial_payment,
            #             name=payment_currency.name))
            # if payment_id.partner_type == "supplier":
            #     # total_partial_payment = - total_partial_payment
            #     if total_partial_payment - (partial_payment + self.done_discount_amount) < -0.001:
            #         str_error = 'Invoice [{number}] , (Partial payment + Discount) ' \
            #                     'must be less or equal to To-Pay : {total_partial_payment} {name}.'
            #         raise ValidationError(str_error.format(
            #             number=self.invoice_id.name,
            #             total_partial_payment=total_partial_payment,
            #             name=payment_currency.name))

            self.partial_payment = partial_payment

    @api.model
    def create(self, vals):
        payment_in_id = vals.get('payment_in_id', False)
        if payment_in_id:
            vals['payment_id'] = payment_in_id
        return super(account_payment_partial, self).create(vals)
