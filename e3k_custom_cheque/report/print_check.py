# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date
from datetime import datetime
import re
import logging

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

    def _compute_is_e3k_partial_payment_installed(self):
        for payment in self:
            is_installed = False
            module_installed = self.env['ir.module.module'].sudo().search([('name', '=', 'e3k_partial_payment'),
                                                                           ('state', '=', 'installed')])
            if module_installed:
                is_installed = True
            payment.is_e3k_partial_payment_installed = is_installed

    def do_print_checks(self):
        if self:
            check_layout = self[0].company_id.account_check_printing_layout
            if check_layout != 'disabled' and self[0].journal_id.company_id.country_id.code in ('US', 'CA'):
                return self.env.ref('%s' % check_layout).report_action(self)

    def _check_build_page_info(self, i, p):
        page = super(report_print_check, self)._check_build_page_info(i, p)
        payment_date_1 = fields.Date.from_string(self.date)
        payment_date = datetime.strftime(payment_date_1, str(self.company_id.date_format))
        date_format_text = self.company_id.date_format
        date_format_text = re.sub(r'[^a-zA-Z ]', "", date_format_text)
        date_format_text = date_format_text.upper()
        if 'fr_' in self.partner_id.lang:
            date_format_text = date_format_text.replace('D', 'J' * 2)
            date_format_text = date_format_text.replace('M', 'M' * 2)
            date_format_text = date_format_text.replace('Y', 'A' * 4)
        if 'fr_' not in self.partner_id.lang:
            date_format_text = date_format_text.replace('D', 'D' * 2)
            date_format_text = date_format_text.replace('M', 'M' * 2)
            date_format_text = date_format_text.replace('Y', 'Y' * 4)

        payment_date_str = ''
        for lettre in payment_date:
            payment_date_str += lettre + ' '

        if len(payment_date_str) and (payment_date_str[len(payment_date_str) - 1] == ' '):
            payment_date_str = payment_date_str[0:len(payment_date_str) - 1]
            if self.company_id.is_currency:
                amount = formatLang(self.env, self.amount, currency_obj=self.currency_id) if i == 0 else 'VOID'
            else:
                amount = formatLang(self.env, self.amount, currency_obj=False) if i == 0 else 'VOID'

        page.update({
            'payment_amount_2': formatLang(self.env, self.amount, currency_obj=self.currency_id) if i == 0 else 'VOID',
            'amount': amount,
            'company_id': self.company_id,
            'partner_street1': self.partner_id.street,
            'partner_street2': self.partner_id.street2,
            'partner_city': self.partner_id.city,
            'partner_zip': self.partner_id.zip,
            'partner_state': self.partner_id.state_id and self.partner_id.state_id.name or False,
            'payment_date': payment_date,
            'payment_date_2': payment_date_str,
            'payment_date_canada': format_date(self.env, self.date, str(self.company_id.date_format)),
            'partner_lang': self.partner_id.lang,
            'date_format_text': date_format_text,
            'check_number': self.check_number,
        })
        return page

    def _check_make_stub_line(self, invoice):
        """ Return the dict used to display an invoice/refund in the stub """
        lines = super(report_print_check, self)._check_make_stub_line(invoice)
        lines.update({
            'invoice_date': format_date(self.env, invoice.invoice_date),
            'number': invoice.ref if invoice.ref else '',
        })
        return lines

    def _check_make_stub_line_payment(self, payment):
        """ Return the dict used to display an invoice/refund in the stub """
        return {
            'invoice_date': format_date(self.env, payment.invoice_date),
            'due_date': format_date(self.env, payment.invoice_date_due),
            # 'number': payment.ref and payment.name + ' - ' + payment.refe or payment.name,
            'number': payment.ref if payment.ref else '',
            'amount_total': formatLang(self.env, payment.amount_total_signed,
                                       currency_obj=payment.invoice_id.currency_id),
            'amount_residual': formatLang(self.env, payment.amount_residual_signed,
                                          currency_obj=payment.currency_id) if payment.amount_residual_signed * 10 ** 4 != 0 else '-',
            'amount_paid': formatLang(self.env, payment.partial_payment,
                                      currency_obj=payment.currency_id),
            'currency': payment.currency_id,
        }

    # def _check_make_stub_pages(self):
    #     """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
    #         first page is valid. This function returns a list of stub lines per page.
    #     """
    #     if len(self.move_id._get_reconciled_invoices()) == 0:
    #         return None
    #
    #     multi_stub = self.company_id.account_check_printing_multi_stub
    #     INV_LINES_PER_STUB = self.company_id.check_inv_line_per_page
    #     if (self.is_e3k_partial_payment_installed):
    #         stub_lines = [self._check_make_stub_line_payment(pay) for pay in
    #                       self.payment_partial_ids.sorted(key=lambda r: (r.invoice_date_due or r.invoice_date, r.id))]
    #         print('yesyest')
    #         print("stub_lines")
    #         print(self.payment_partial_ids)
    #
    #
    #     else:
    #
    #         invoices = self.move_id._get_reconciled_invoices().sorted(
    #             key=lambda r: r.invoice_date_due or fields.Date.context_today(self))
    #         print("invoices")
    #         print(invoices)
    #         stub_lines = [self._check_make_stub_line(inv) for inv in invoices]
    #
    #     # Crop the stub lines or split them on multiple pages
    #     if not multi_stub:
    #         # If we need to crop the stub, leave place for an ellipsis line
    #         num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
    #         stub_pages = [stub_lines[:num_stub_lines]]
    #     else:
    #         stub_pages = []
    #         i = 0
    #         while i < len(stub_lines):
    #             # Make sure we don't start the credit section at the end of a page
    #             if len(stub_lines) >= i + INV_LINES_PER_STUB and stub_lines[i + INV_LINES_PER_STUB - 1].get('header'):
    #                 num_stub_lines = INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
    #             else:
    #                 num_stub_lines = INV_LINES_PER_STUB
    #             stub_pages.append(stub_lines[i:i + num_stub_lines])
    #             i += num_stub_lines
    #     return stub_pages
