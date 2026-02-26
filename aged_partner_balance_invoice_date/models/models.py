# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.addons.account.models.account_account import AccountAccount
from odoo.tools.misc import format_date
from .aged_balance import get_aged_partner_balance_data


def is_account_in_company_currency(account: AccountAccount) -> bool:
    return not account.currency_id or account.currency_id == account.company_id.currency_id


# class ReportAgedPartnerBalance(models.AbstractModel):

#     _inherit = 'report.account.report_agedpartnerbalance'

#     def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):
#         move_states = ["posted"] if target_move == "posted" else ["draft", "posted"]

#         accounts = self.env['account.account'].search([
#             ('internal_type', 'in', account_type),
#         ])

#         filtered_accounts = self.env.context.get('filtered_accounts')
#         if filtered_accounts:
#             accounts = accounts & filtered_accounts

#         use_account_currency = self.env.context.get('use_account_currency', False)

#         # When using the account currency option, at least one account
#         # must be selected. Otherwise, an empty aged balance is shown.
#         if use_account_currency and not filtered_accounts:
#             accounts = self.env['account.account'].browse([])

#         # If the selected account is in the company currency,
#         # then use_account_currency is forced.
#         force_company_currency = any(is_account_in_company_currency(a) for a in accounts)

#         return get_aged_partner_balance_data(
#             env=self.env,
#             date_from=date_from,
#             accounts=accounts,
#             move_states=move_states,
#             use_account_currency=use_account_currency and not force_company_currency,
#             use_maturity_date=self.env.context.get('use_maturity_date', True),
#         )


class AccountAgedPartnerWithAccountCurrency(models.AbstractModel):

    _inherit = 'account.aged.partner'

    # def format_value(self, value, currency=False):
    #     if self.env.context.get('use_account_currency'):
    #         accounts = self.env.context.get('filtered_accounts')
    #         currency = (
    #             accounts[0].currency_id or accounts[0].company_id.currency_id
    #             if accounts else None
    #         )
    #     return super().format_value(value, currency=currency)

    @api.model
    def get_lines(self, options, line_id=None):
        account = options.get('account')
        self = self.with_context(
            use_account_currency=options.get('use_account_currency', False),
            filtered_accounts=(
                self.env['account.account'].browse(int(account[0])) if account else None
            ),
        )
        return super(AccountAgedPartnerWithAccountCurrency, self).get_lines(options, line_id)

    @api.model
    def get_options(self, previous_options=None):
        """Add the options related to the currency selection.

        use_account_currency::

            This option is a switch between the company and foreign currency.
            If enabled, the displayed currency will be the account's currency.
            Otherwise, the currency of the general ledger (the company currency) is used.

        account::

            This options specifies a specific account to filter the report.
            It contains the name_get tuple of the account (ID, display_name).

        available_accounts::

            This option specifies the accounts available for filtering the report.
            It contains a list of name_get tuples.
        """
        options = super().get_options(previous_options)
        options['use_account_currency'] = (
            (previous_options or {}).get('use_account_currency', False)
        )
        options['account'] = (previous_options or {}).get('account', None)

        account_type = 'receivable' if self._name == 'account.aged.receivable' else 'payable'
        available_accounts = self.env['account.account'].search(
            [('internal_type', '=', account_type)]
        ).sorted(lambda a: a.display_name)
        options['available_accounts'] = available_accounts.name_get()
        return options


class ReportAccountAgedPartnerWithInvoiceDateBasis(models.AbstractModel):

    _inherit = 'account.aged.partner'

    @api.model
    def get_options(self, previous_options=None):
        """Add `use_maturity_date` to the report options.

        The option defaults to True, meaning that if not specified otherwise by the user,
        the aged balance will be presented with the maturity date as basis.
        """
        options = super().get_options(previous_options)
        options['use_maturity_date'] = (previous_options or {}).get('use_maturity_date', True)
        return options

    def _get_current_column_name(self, options):
        """Get the label to display in the current column.

        Note that in vanilla Odoo the term `Not due on` is used instead of `Current`.
        This label was changed because `Current` is the standard term used in the industry.

        :param options: the report options
        """
        formated_date = format_date(self.env, options['date']['date'])
        return _('Current {}').format(formated_date)

    def get_columns_name(self, options):
        """Hide the `Current` column if report is not based on maturity date.

        If the report is based on maturity date, we get::

            | <Empty> | Current yyyy/mm/dd | 0 - 30 | 30 - 60 | 60 - 90 | Older | Total |

        Otherwise, if the report is based on invoice date, we get::

            | <Empty> | 0 - 30 | 30 - 60 | 60 - 90 | Older | Total |
        """
        all_column_names = super().get_columns_name(options)
        all_column_names[1]['name'] = self._get_current_column_name(options)
        return (
            all_column_names if options.get('use_maturity_date', True) else
            all_column_names[0:1] + all_column_names[2:]
        )

    @api.model
    def get_lines(self, options, line_id=None):
        """Enable displaying the aged balance based on the invoice date.

        If use_maturity_date is disabled, the report is displayed based on the maturity date.
        """
        use_maturity_date = options.get('use_maturity_date', True)
        self = self.with_context(use_maturity_date=use_maturity_date)
        result = super(
            ReportAccountAgedPartnerWithInvoiceDateBasis, self).get_lines(options, line_id)

        if not use_maturity_date:
            for line in result:
                line['columns'] = line['columns'][1:]

        return result
