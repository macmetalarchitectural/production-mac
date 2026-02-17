# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools.misc import format_date, formatLang

INV_LINES_PER_STUB = 7


class ReportPrintCheck(models.Model):
    _inherit = 'account.payment'

    def calculate_discount_payment(self):
        cash_discount_account = self.company_id.account_journal_early_pay_discount_gain_account_id
        credit = sum(self.move_id.line_ids.filtered(lambda r: r.account_id == cash_discount_account).mapped('credit'))
        if credit:
            return float(credit)
        return False

    @api.depends('payment_method_line_id', 'currency_id', 'amount')
    def _compute_check_amount_in_words(self):
        for pay in self:
            if pay.currency_id:
                pay.check_amount_in_words = pay.currency_id.with_context(
                    lang=pay.partner_id.lang or 'fr_CA'
                ).amount_to_text(pay.amount)
            else:
                pay.check_amount_in_words = False

    def _check_build_page_info(self, i, p):
        page = super()._check_build_page_info(i, p)
        date = self.date
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"
        journal_id = self.journal_id
        format = journal_id.date_format_str
        payment_date_2 = format.replace('dd', day).replace('mm', month).replace('YYYY', str(date.year))
        amout_without_currency = page['amount']
        company_id = self.company_id
        currency_id = self.currency_id
        partner_id = self.partner_id
        if not company_id.print_currency_sign:
            page['amount'] = page['amount'].replace(currency_id.symbol, "")
            amout_without_currency = page['amount'].replace(currency_id.symbol, "")

        page.update(
            {
                'payment_amount_2': formatLang(self.env, self.amount, currency_obj=currency_id) if i == 0 else 'VOID',
                'company_id': company_id,
                'partner_street1': partner_id.street,
                'partner_street2': partner_id.street2,
                'partner_city': partner_id.city,
                'partner_zip': partner_id.zip,
                'partner_state': partner_id.state_id.name or False,
                'check_number': self.check_number,
                'payment_date': payment_date_2,
                'date_format_str': journal_id.date_format_str,
                'display_date_format_str_top': company_id.display_date_format_top + 20,
                'amout_without_currency': amout_without_currency,
            }
        )
        return page

    def get_total_epd_amount(self, invoice):
        """
        Retourne la somme totale des escomptes d'une facture (Odoo 19)
        en utilisant la méthode native qui calcule les counterpart AMLs.
        """

        total_discount = 0.0
        if invoice.invoice_payment_term_id and invoice.invoice_payment_term_id.early_discount:
            res = invoice._get_invoice_counterpart_amls_for_early_payment_discount_per_payment_term_line()  # noqa
            term_lines = res.get("term_lines", {})

            for __, account_map in term_lines.items():
                for __, values in account_map.items():
                    amount = values.get("amount_currency") or 0.0
                    total_discount += amount

        return abs(total_discount)

    def _check_make_stub_pages(self):
        """The stub is the summary of paid invoices. It may spill on several pages,
        in which case only the check on first page is valid. This function returns
        a list of stub lines per page.
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
                amount_residual_str = formatLang(
                    self.env,
                    invoice_sign * invoice.amount_residual,
                    currency_obj=invoice.currency_id,
                )
            amount_p = invoice_sign * (invoice.amount_total - invoice.amount_residual)
            escompt = self.get_total_epd_amount(invoice)
            escompt_curr = formatLang(self.env, escompt, currency_obj=self.currency_id)
            amount_paid = formatLang(self.env, amount_p - escompt, currency_obj=self.currency_id)
            disc = 0.0

            return {
                'invoice_date': format_date(self.env, invoice.invoice_date),
                'number': number,
                'amount_total': formatLang(
                    self.env,
                    invoice_sign * invoice.amount_total,
                    currency_obj=invoice.currency_id,
                ),
                'amount_residual': amount_residual_str,
                'amount_paid': formatLang(
                    self.env,
                    invoice_sign * sum(partials.mapped(partial_field)),
                    currency_obj=self.currency_id,
                ),
                'disc': formatLang(self.env, disc, currency_obj=self.currency_id),
                'escompt': escompt_curr,
                'p_amount_paid': amount_paid,
                'currency': invoice.currency_id,
            }

        # Decode the reconciliation to keep only invoices.
        term_lines = self.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
        )
        invoices = (
            term_lines.matched_debit_ids.debit_move_id.move_id + term_lines.matched_credit_ids.credit_move_id.move_id
        ).filtered(lambda x: x.is_outbound())

        invoices = invoices.sorted(lambda x: x.invoice_date_due or x.date)
        partials = self.move_id._get_reconciled_invoices_partials()[0] if self.move_id else []
        invoices_partials = [partial[2].move_id for partial in partials]
        payment_refund = []
        for x in invoices_partials:
            invs = x._get_reconciled_invoices_partials()[0]
            if invs:
                for refunds in invs:
                    if refunds != self.move_id:
                        payment_refund.append(refunds[2].move_id)
        if payment_refund:
            for refund in payment_refund:
                invoices += refund

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
            stub_lines += [
                prepare_vals(invoice, partials)
                for invoice, partials in invoice_map.items()
                if invoice.move_type == 'in_invoice'
            ]
            # stub_lines += [{'header': True, 'name': "Refunds"}]
            stub_lines += [
                prepare_vals(invoice, partials)
                for invoice, partials in invoice_map.items()
                if invoice.move_type in ['out_refund', 'in_refund']
            ]
        else:
            stub_lines = [
                prepare_vals(invoice, partials)
                for invoice, partials in invoice_map.items()
                if invoice.move_type == 'in_invoice'
            ]

        # Crop the stub lines or split them on multiple pages
        if not self.company_id.account_check_printing_multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = INV_LINES_PER_STUB - 1 if len(stub_lines) > INV_LINES_PER_STUB else INV_LINES_PER_STUB
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
                stub_pages.append(stub_lines[i : i + num_stub_lines])  # noqa
                i += num_stub_lines

        return stub_pages
