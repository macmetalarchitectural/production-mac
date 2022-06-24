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

    payment_invoice_id = fields.Many2one('account.move', string='Payment for invoice', readonly=True , ondelete='cascade')
    partial_payment_line_id = fields.Many2one('account.payment.partial', string="Partial Payment Line" , ondelete='cascade')

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


    def _prepare_reconciliation_partials(self):
        res = super(AccountMoveLine, self)._prepare_reconciliation_partials()
        if 'default_amount' in self._context:
            pp_amount = self._context['default_amount']
            debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0))

            credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0))
            debit_line = None
            credit_line = None

            debit_amount_residual = 0.0
            debit_amount_residual_currency = 0.0
            credit_amount_residual = 0.0
            credit_amount_residual_currency = 0.0
            debit_line_currency = None
            credit_line_currency = None

            partials_vals_list = []
            i = 0
            while True:

                # Move to the next available debit line.
                if not debit_line:
                    debit_line = next(debit_lines, None)
                    if not debit_line:
                        break

                    debit_amount_residual = debit_line.amount_residual

                    if debit_line.currency_id:
                        debit_amount_residual_currency = debit_line.amount_residual_currency
                        debit_line_currency = debit_line.currency_id
                    else:
                        debit_amount_residual_currency = debit_amount_residual
                        debit_line_currency = debit_line.company_currency_id

                # Move to the next available credit line.
                if not credit_line:
                    credit_line = next(credit_lines, None)
                    if not credit_line:
                        break

                    credit_amount_residual = -pp_amount #-credit_line.amount_residual

                    if credit_line.currency_id:
                        credit_amount_residual_currency = -pp_amount #credit_line.amount_residual_currency
                        credit_line_currency = credit_line.currency_id
                    else:
                        credit_amount_residual_currency = credit_amount_residual
                        credit_line_currency = credit_line.company_currency_id
                # if i == 0:
                # #     # debit_amount_residual = -pp_amount
                #     credit_amount_residual = pp_amount
                min_amount_residual = min(debit_amount_residual, -credit_amount_residual)
                has_debit_residual_left = not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
                has_credit_residual_left = not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
                has_debit_residual_curr_left = not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
                has_credit_residual_curr_left = not credit_line_currency.is_zero(credit_amount_residual_currency) and credit_amount_residual_currency < 0.0

                if debit_line_currency == credit_line_currency:
                    # Reconcile on the same currency.

                    # The debit line is now fully reconciled because:
                    # - either amount_residual & amount_residual_currency are at 0.
                    # - either the credit_line is not an exchange difference one.
                    if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
                        debit_line = None
                        continue

                    # The credit line is now fully reconciled because:
                    # - either amount_residual & amount_residual_currency are at 0.
                    # - either the debit is not an exchange difference one.
                    if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
                        credit_line = None
                        continue

                    min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
                    min_debit_amount_residual_currency = min_amount_residual_currency
                    min_credit_amount_residual_currency = min_amount_residual_currency

                else:
                    # Reconcile on the company's currency.

                    # The debit line is now fully reconciled since amount_residual is 0.
                    if not has_debit_residual_left:
                        debit_line = None
                        continue

                    # The credit line is now fully reconciled since amount_residual is 0.
                    if not has_credit_residual_left:
                        credit_line = None
                        continue

                    min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
                        min_amount_residual,
                        debit_line.currency_id,
                        credit_line.company_id,
                        credit_line.date,
                    )
                    min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
                        min_amount_residual,
                        credit_line.currency_id,
                        debit_line.company_id,
                        debit_line.date,
                    )

                debit_amount_residual -= min_amount_residual
                debit_amount_residual_currency -= min_debit_amount_residual_currency
                credit_amount_residual += min_amount_residual
                credit_amount_residual_currency += min_credit_amount_residual_currency
                partials_vals_list.append({
                    'amount': min_amount_residual,
                    'debit_amount_currency': min_debit_amount_residual_currency,
                    'credit_amount_currency': min_credit_amount_residual_currency,
                    'debit_move_id': debit_line.id,
                    'credit_move_id': credit_line.id,
                })


            return partials_vals_list

        else:
            return res


