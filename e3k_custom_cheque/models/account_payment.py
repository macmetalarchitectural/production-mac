# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    show_ref_on_check = fields.Boolean()  # no-check

    def _check_build_page_info(self, i, p):
        page_info = super()._check_build_page_info(i, p)
        page_info['show_ref_on_check'] = self.show_ref_on_check
        memo = self.memo
        if memo:
            page_info['ref_lines'] = memo.split('\n')
            longest_line = max(memo.split('\n'), key=len)
            page_info['ref_width'] = len(longest_line) * self.company_id.check_ref_font_size * 1.2
        else:
            page_info['ref_lines'] = []
            page_info['ref_width'] = 0

        return page_info

    @api.constrains('memo')
    def _check_three_line_limit(self):
        for record in self.filtered(lambda r: r.memo):
            lines = record.memo.split('\n')
            if len(lines) > 3:
                raise ValidationError(_("The ref field cannot exceed three lines."))

            # longest_line = max(lines, key=len)
            # if len(longest_line) > 45:
            #     raise ValidationError(_("One of the lines in the ref field is too long."))

    def print_checks(self):
        """Check that the recordset is valid, set the payments state
        to sent and call print_checks()"""

        # Since this method can be called via a client_action_multi,
        # we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_line_id.code == 'check_printing' and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(
                _(
                    "Payments to print as a checks must have 'Check' selected "
                    "as payment method and not have already been reconciled"
                )
            )
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            self.env.cr.execute(
                """
                  SELECT payment.id
                    FROM account_payment payment
                    JOIN account_move move ON movE.id = payment.move_id
                   WHERE payment.journal_id = %(journal_id)s
                   AND check_number IS NOT NULL
                ORDER BY payment.id::INTEGER DESC
                   LIMIT 1
            """,
                {
                    'journal_id': self.journal_id.id,
                },
            )
            last_printed_check = self.browse(self.env.cr.fetchone())
            # number_len = len(last_printed_check.check_number or "")
            next_check_number = int(last_printed_check.check_number) + 1

            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                },
            }

        self.filtered(lambda r: r.state == 'draft').action_post()
        return self.do_print_checks()
