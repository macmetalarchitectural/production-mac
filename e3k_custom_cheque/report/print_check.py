# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date
from datetime import datetime
import re
import logging

INV_LINES_PER_STUB = 7

# import inflect  # to installe withe python3 => pip install inflect
_logger = logging.getLogger(__name__)
try:
    import inflect
except ImportError:
    _logger.warning(
        "The `inflect` Python module is not installed")

LINE_FILLER = '*'


# INV_LINES_PER_STUB = 7


class report_print_check(models.Model):
    """
    TODO: improved inherited method(overwrite)
    """
    _inherit = 'account.payment'

    is_e3k_partial_payment_installed = fields.Boolean(compute="_compute_is_e3k_partial_payment_installed")

    @api.depends('payment_method_line_id', 'currency_id', 'amount')
    def _compute_check_amount_in_words(self):
        for pay in self:
            if pay.currency_id:
                pay.check_amount_in_words = pay.currency_id.amount_to_text(pay.amount, pay.partner_id.lang)
            else:
                pay.check_amount_in_words = False

    def _compute_is_e3k_partial_payment_installed(self):
        for payment in self:
            is_installed = False
            module_installed = self.env['ir.module.module'].sudo().search([('name', '=', 'e3k_partial_payment'),
                                                                           ('state', '=', 'installed')])
            if module_installed:
                is_installed = True
            payment.is_e3k_partial_payment_installed = is_installed

    def do_print_checks(self):
        check_layout = self.company_id.account_check_printing_layout
        if check_layout != 'disabled' and self.journal_id.company_id.country_id.code in ('US', 'CA'):
            return self.env.ref('%s' % check_layout).report_action(self)

    def _check_build_page_info(self, i, p):
        page = super(report_print_check, self)._check_build_page_info(i, p)
        if len(str(self.date.month)) == 1:
            month = '0' + str(self.date.month)
        else:
            month = str(self.date.month)
        if len(str(self.date.day)) == 1:
            day = '0' + str(self.date.day)
        else:
            day = str(self.date.day)
        format = self.journal_id.date_format_str
        payment_date_2 = format.replace('dd', day).replace('mm', month).replace('YYYY', str(self.date.year))
        page.update({
            'payment_amount_2': formatLang(self.env, self.amount, currency_obj=self.currency_id) if i == 0 else 'VOID',
            'company_id': self.company_id,
            'partner_street1': self.partner_id.street,
            'partner_street2': self.partner_id.street2,
            'partner_city': self.partner_id.city,
            'partner_zip': self.partner_id.zip,
            'partner_state': self.partner_id.state_id and self.partner_id.state_id.name or False,
            'check_number': self.check_number,
            'payment_date': payment_date_2,
        })
        return page

    def _check_make_stub_pages(self):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        self.ensure_one()

        def prepare_vals(invoice, partials):
            number = ' - '.join([invoice.name, invoice.ref] if invoice.ref else [invoice.name])

            if invoice.is_outbound():
                invoice_sign = 1
                partial_field = 'debit_amount_currency'
            else:
                invoice_sign = -1
                partial_field = 'credit_amount_currency'

            if invoice.currency_id.is_zero(invoice.amount_residual):
                amount_residual_str = '-'
            else:
                amount_residual_str = formatLang(self.env, invoice_sign * invoice.amount_residual,
                                                 currency_obj=invoice.currency_id)
            disc = 0.0
            if self.payment_partial_ids:
                disc_mapped = self.payment_partial_ids.filtered(lambda r: r.invoice_id == invoice)
                disc = disc_mapped[0].done_discount_amount_in_out_refund

            if self.payment_partial_ids:
                mapped_p_payment = self.payment_partial_ids.filtered(lambda r:r.invoice_id == invoice)
                amount_paid = formatLang(self.env, invoice_sign * (mapped_p_payment[0].partial_payment),
                                            currency_obj=self.currency_id)
            else:
                amount_paid = formatLang(self.env, invoice_sign * (invoice.amount_total - invoice.amount_residual),
                                            currency_obj=self.currency_id)
            return {
                'invoice_date': format_date(self.env, invoice.invoice_date),
                'number': number,
                'amount_total': formatLang(self.env, invoice_sign * invoice.amount_total,
                                           currency_obj=invoice.currency_id),
                'amount_residual': amount_residual_str,
                'amount_paid': formatLang(self.env, invoice_sign * sum(partials.mapped(partial_field)),
                                          currency_obj=self.currency_id),
                'disc': formatLang(self.env, disc,
                                            currency_obj=self.currency_id),

                'p_amount_paid': amount_paid,
                'currency': invoice.currency_id,
            }

        # Decode the reconciliation to keep only invoices.
        term_lines = self.line_ids.filtered(lambda line: line.account_id.internal_type in ('receivable', 'payable'))
        invoices = (
                    term_lines.matched_debit_ids.debit_move_id.move_id + term_lines.matched_credit_ids.credit_move_id.move_id) \
            .filtered(lambda x: x.is_outbound())
        if self.payment_partial_ids:
            invoices = self.payment_partial_ids.mapped('invoice_id')
        invoices = invoices.sorted(lambda x: x.invoice_date_due or x.date)

        # Group partials by invoices.
        invoice_map = {invoice: self.env['account.partial.reconcile'] for invoice in invoices}
        for partial in term_lines.matched_debit_ids:
            invoice = partial.debit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial
        for partial in term_lines.matched_credit_ids:
            invoice = partial.credit_move_id.move_id
            if invoice in invoice_map:
                invoice_map[invoice] |= partial

        # Prepare stub_lines.
        if 'out_refund' in invoices.mapped('move_type') or 'in_refund' in invoices.mapped('move_type'):
            stub_lines = []
            stub_lines += [prepare_vals(invoice, partials)
                           for invoice, partials in invoice_map.items()
                           if invoice.move_type == 'in_invoice']
            # stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += [prepare_vals(invoice, partials)
                           for invoice, partials in invoice_map.items()
                           if invoice.move_type in ['out_refund', 'in_refund']]
        else:
            stub_lines = [prepare_vals(invoice, partials)
                          for invoice, partials in invoice_map.items()
                          if invoice.move_type == 'in_invoice']

        # Crop the stub lines or split them on multiple pages
        if not self.company_id.account_check_printing_multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                line_per_stub = self.company_id.check_inv_line_per_page
                if len(stub_lines) >= i + line_per_stub and stub_lines[i + line_per_stub - 1].get('header'):
                    num_stub_lines = line_per_stub - 1 or line_per_stub
                else:
                    num_stub_lines = line_per_stub
                stub_pages.append(stub_lines[i:i + num_stub_lines])
                i += num_stub_lines

        return stub_pages