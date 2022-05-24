# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_sequence = fields.Integer(default=1, string='Payment sequence',
                                      help="Gives the sequence of this invoice during the payment process.")
    payment_discount_amount = fields.Monetary(string='Discount Amount', compute='_compute_payment_discount_amount')
    due_payment_discount_amount = fields.Monetary(string='Due Discount Amount',
                                                  compute='_compute_payment_discount_amount')
    net_amount_invoice = fields.Monetary(string='Net Amount', compute='_get_net_amount_invoice')
    date_discount = fields.Date(string='Discount End Date', compute='_get_date_discount', readonly=True)

    def _get_date_discount(self):

        for move in self:
            move.date_discount = False
            if move.invoice_date:
                move.date_discount = move.invoice_date
                if move.invoice_payment_term_id and move.invoice_payment_term_id.number_discount_days:
                    # invoice_date = datetime.strptime(move.invoice_date, DEFAULT_SERVER_DATE_FORMAT)
                    move.date_discount = move.invoice_date + timedelta(
                        days=move.invoice_payment_term_id.number_discount_days)

    def _compute_payment_discount_amount(self):
        for move in self:
            move_payment_ids = []
            reconciled_vals = move._get_reconciled_info_JSON_values()

            if reconciled_vals:
                for element in reconciled_vals:
                    if element.get('account_payment_id'):
                        if element.get('account_payment_id') not in move_payment_ids:
                            move_payment_ids.append(element.get('account_payment_id'))

            if move.invoice_payment_term_id and move.invoice_payment_term_id.payment_discount_percent and move.invoice_payment_term_id.payment_term_discount_ids:
                move.payment_discount_amount = move.net_amount_invoice * move.invoice_payment_term_id.payment_discount_percent / 100.0
                done_discount_amount = 0.0
                if move_payment_ids:
                    move_payment_ids = self.env["account.payment"].browse(move_payment_ids)
                    for payment in move_payment_ids:
                        if payment.state in ('posted', 'reconciled'):
                            for payment_line in payment.payment_partial_ids:
                                if payment_line.invoice_id and (payment_line.invoice_id.id == move.id):
                                    done_discount_amount += payment_line.done_discount_amount_signed

                move.due_payment_discount_amount = move.payment_discount_amount - done_discount_amount
            else:
                move.due_payment_discount_amount = 0.0
                move.payment_discount_amount = 0.0

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        list_args = []
        if self._context:
            context = self._context
            if context.get('active_model') and (context.get('active_model') == 'account.invoice.import.wizard'):
                return super(AccountMove, self).search(args, offset, limit, order, count=count)

        for arg in args:
            arg2 = arg
            if arg2 and (len(arg2) == 3) and arg2[0] and (arg2[0] == 'id') and arg2[1] and (arg2[1] == 'not in') and \
                    arg2[2] and (len(arg2[2]) == 1) and (len(str(arg2[2][0])) == 3) and (
            not isinstance(arg2[2][0], (int))):
                arg2 = ['id', 'not in', arg2[2][0][2]]
            #     and (not isinstance(arg2[2][0][2], int))
            if arg2 and (len(arg2) == 3) and arg2[0] and (arg2[0] == 'partner_id') and arg2[1] and (arg2[1] == 'in') and \
                    arg2[2] and isinstance(arg2[2], str):
                str_partner_ids = arg2[2]
                str_partner_ids = str_partner_ids.replace('[', '').replace(']', '').replace(' ', '').split(',')
                new_partner_ids = []
                for str_id in str_partner_ids:
                    new_partner_ids.append(int(str_id))
                arg2 = ['partner_id', 'in', new_partner_ids]

            list_args.append(arg2)
        #         [u'partner_id', u'in', [[6, False, [22, 23, 33, 18, 8]]]]
        if self._context:
            context = self._context
            if context.get('payment_type') and (context['payment_type'] == 'inbound'):
                list_args.append(['type', 'in', ['out_invoice', 'out_refund']])
            elif context.get('payment_type') and (context['payment_type'] == 'outbound'):
                list_args.append(['type', 'in', ['in_invoice', 'in_refund']])

        if list_args:
            args = list_args
        #_logger.error("e3k_advanced_payment testing submodule")
        res = super(AccountMove, self).search(args, offset, limit, order, count=count)
        return res

    @api.depends('invoice_line_ids')
    def _get_net_amount_invoice(self):
        for move in self:
            net_amount_invoice = move.amount_untaxed_signed
            # used_invoice_line_ids = []
            # for inv_line in move.invoice_line_ids:
            #     if inv_line.product_id and (
            #             inv_line.product_id.categ_id in move.invoice_payment_term_id.product_category_ids):
            #         used_invoice_line_ids.append(inv_line.id)
            #         net_amount_invoice -= inv_line.price_subtotal_signed
            move.net_amount_invoice = net_amount_invoice

    def name_get(self):
        TYPES = {

            'entry': _('Journal Entry'),
            'out_receipt': _('Sales Receipt'),
            'in_receipt': _('Purchase Receipt'),
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Refund'),
            'in_refund': _('Vendor Refund'),
        }
        result = []
        payment_reference = ''
        for inv in self:
            if inv.payment_reference != inv.name:
                payment_reference = inv.payment_reference
            result.append(
                (inv.id, "%s %s %s" % (inv.ref or '', inv.name or TYPES[inv.move_type], payment_reference or '')))
        return result


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_invoice_id = fields.Many2one('account.move', string='Payment for invoice', readonly=True)
    partial_payment_line_id = fields.Many2one('account.payment.partial', string="Partial Payment Line")
    _sql_constraints = [
        (
            'check_credit_debit',
            'CHECK(credit + debit>=0 AND credit * debit=0)',
            'Wrong credit or debit value in accounting entry !'
        ),
        (
            'check_accountable_required_fields',
             "CHECK(COALESCE(display_type IN ('line_section', 'line_note'), 'f') OR account_id IS NOT NULL)",
             "Missing required account on accountable invoice line."
        ),
        (
            'check_non_accountable_fields_null',
             "CHECK(display_type NOT IN ('line_section', 'line_note') OR (amount_currency = 0 AND debit = 0 AND credit = 0 AND account_id IS NULL))",
             "Forbidden unit price, account and quantity on non-accountable invoice line"
        ),
        (
            'check_amount_currency_balance_sign',
            '''CHECK(
                1=1
            )''',
            "The amount expressed in the secondary currency must be positive when account is debited and negative when "
            "account is credited. If the currency is the same as the one from the company, this amount must strictly "
            "be equal to the balance."
        ),
    ]
    def _update_check(self):
        """
        Raise Warning to cause rollback if the move is posted,
        some entries are reconciled or the move is older than the lock date
        """
        move_ids = set()
        for line in self:
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state != 'draft':
                raise UserError(_(
                    'You cannot do this modification on a posted journal entry, you can just change some non legal fields. You must revert the journal entry to cancel it.\n%s.') % err_msg)
            if line.reconciled and not ((abs(line.debit) < 0.0001) and (abs(line.credit) < 0.0001)):
                raise UserError(_(
                    'You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            if line.move_id.id not in move_ids:
                move_ids.add(line.move_id.id)
            self.env['account.move'].browse(list(move_ids))._check_lock_date()
        return True
