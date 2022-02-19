# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from freezegun import freeze_time
from odoo.tests import common


@freeze_time('2017-12-01')
class TestAgedPartnerBalance(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cad = cls.env.ref('base.CAD')
        cls.usd = cls.env.ref('base.USD')

        cls.report_cls = cls.env['report.account.report_agedpartnerbalance']

        cls.company = cls.env['res.company'].create({
            'name': 'My Company',
            'currency_id': cls.cad.id,
        })

        cls.env.user.write({
            'company_id': cls.company.id,
            'company_ids': [(4, cls.company.id)],
        })

        cls.customer = cls.env['res.partner'].create({
            'name': 'My Customer',
            'customer': True,
        })

        cls.supplier = cls.env['res.partner'].create({
            'name': 'My Supplier',
            'supplier': True,
        })

        cls.sale_journal = cls.env['account.journal'].create({
            'company_id': cls.company.id,
            'name': 'Sales',
            'code': 'SALE',
            'type': 'sale',
        })

        cls.us_sale_journal = cls.env['account.journal'].create({
            'company_id': cls.company.id,
            'name': 'Sales',
            'code': 'SALEU',
            'type': 'sale',
            'currency_id': cls.usd.id,
        })

        cls.purchase_journal = cls.env['account.journal'].create({
            'company_id': cls.company.id,
            'name': 'Purchases',
            'code': 'PURC',
            'type': 'purchase',
        })

        cls.us_purchase_journal = cls.env['account.journal'].create({
            'company_id': cls.company.id,
            'name': 'Purchases',
            'code': 'PURCU',
            'type': 'purchase',
            'currency_id': cls.usd.id,
        })

        cls.bank_journal = cls.env['account.journal'].create({
            'company_id': cls.company.id,
            'name': 'Bank',
            'code': 'BNK',
            'type': 'bank',
        })

        cls.us_bank_journal = cls.env['account.journal'].create({
            'company_id': cls.company.id,
            'name': 'Bank US',
            'code': 'BNKU',
            'type': 'bank',
            'currency_id': cls.usd.id,
        })

        cls.company.currency_exchange_journal_id = \
            cls.env['account.journal'].create({
                'company_id': cls.company.id,
                'name': 'Exchange Rate',
                'code': 'EXCH',
                'type': 'general',
            })

        cls.exchange_account = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Exchange Gain/Loss',
            'code': '710000',
            'user_type_id':
            cls.env.ref('account.data_account_type_other_income').id,
        })

        cls.company.income_currency_exchange_account_id = cls.exchange_account
        cls.company.expense_currency_exchange_account_id = cls.exchange_account

        cls.receivable = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Receivable',
            'code': '110100',
            'user_type_id': cls.env.ref(
                'account.data_account_type_receivable').id,
            'reconcile': True,
        })

        cls.us_receivable = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Receivable US',
            'code': '110200',
            'user_type_id': cls.env.ref(
                'account.data_account_type_receivable').id,
            'currency_id': cls.usd.id,
            'reconcile': True,
        })

        cls.payable = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Payable',
            'code': '210100',
            'user_type_id': cls.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True,
        })

        cls.us_payable = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Payable US',
            'code': '210200',
            'user_type_id': cls.env.ref(
                'account.data_account_type_payable').id,
            'currency_id': cls.usd.id,
            'reconcile': True,
        })

        cls.income = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Income',
            'code': '410100',
            'user_type_id': cls.env.ref(
                'account.data_account_type_revenue').id,
        })

        cls.expense = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Expense',
            'code': '510100',
            'user_type_id': cls.env.ref(
                'account.data_account_type_expenses').id,
        })

        cls.bank = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Bank',
            'code': '100100',
            'user_type_id': cls.env.ref(
                'account.data_account_type_liquidity').id,
            'currency_id': cls.usd.id,
            'reconcile': True,
        })

        cls.bank_us = cls.env['account.account'].create({
            'company_id': cls.company.id,
            'name': 'Bank',
            'code': '100200',
            'user_type_id': cls.env.ref(
                'account.data_account_type_liquidity').id,
            'currency_id': cls.usd.id,
            'reconcile': True,
        })

        cls.move_1 = cls.env['account.move'].create({
            'name': '/',
            'journal_id': cls.sale_journal.id,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'partner_id': cls.customer.id,
                    'account_id': cls.receivable.id,
                    'debit': 100,
                    'date_maturity': '2018-01-01',
                }),
                (0, 0, {
                    'name': '/',
                    'account_id': cls.income.id,
                    'credit': 100,
                }),
            ]
        })

        cls.move_2 = cls.env['account.move'].create({
            'name': '/',
            'journal_id': cls.us_sale_journal.id,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'partner_id': cls.customer.id,
                    'account_id': cls.us_receivable.id,
                    'debit': 200,
                    'amount_currency': 150,
                    'currency_id': cls.usd.id,
                    'date_maturity': '2018-01-01',
                }),
                (0, 0, {
                    'name': '/',
                    'account_id': cls.income.id,
                    'credit': 200,
                    'amount_currency': -150,
                    'currency_id': cls.usd.id,
                }),
            ]
        })

        cls.move_3 = cls.env['account.move'].create({
            'name': '/',
            'journal_id': cls.purchase_journal.id,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'account_id': cls.expense.id,
                    'debit': 300,
                }),
                (0, 0, {
                    'name': '/',
                    'partner_id': cls.supplier.id,
                    'account_id': cls.payable.id,
                    'credit': 300,
                    'date_maturity': '2018-01-01',
                }),
            ]
        })

        cls.move_4 = cls.env['account.move'].create({
            'name': '/',
            'journal_id': cls.us_purchase_journal.id,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'account_id': cls.expense.id,
                    'debit': 400,
                    'amount_currency': 350,
                    'currency_id': cls.usd.id,
                }),
                (0, 0, {
                    'name': '/',
                    'partner_id': cls.supplier.id,
                    'account_id': cls.us_payable.id,
                    'credit': 400,
                    'amount_currency': -350,
                    'currency_id': cls.usd.id,
                    'date_maturity': '2018-01-01',
                }),
            ]
        })

    def setUp(self):
        super().setUp()
        moves = self.move_1 | self.move_2 | self.move_3 | self.move_4
        moves.mapped('line_ids').refresh()
        moves.refresh()

    def _check_not_due(self, result, expected_amount):
        if result[1]:
            self.assertEqual(result[1][6], expected_amount)
        else:
            self.assertEqual(0, expected_amount)

    def _check_0_30(self, result, expected_amount):
        if result[1]:
            self.assertEqual(result[1][4], expected_amount)
        else:
            self.assertEqual(0, expected_amount)

    def _check_30_60(self, result, expected_amount):
        if result[1]:
            self.assertEqual(result[1][3], expected_amount)
        else:
            self.assertEqual(0, expected_amount)

    def _check_total(self, result, expected_amount):
        if result[1]:
            self.assertEqual(result[1][5], expected_amount)
        else:
            self.assertEqual(0, expected_amount)

    def _create_customer_payment(self, date):
        move = self.env['account.move'].create({
            'name': '/',
            'journal_id': self.bank_journal.id,
            'date': date,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'account_id': self.bank.id,
                    'debit': 100,
                }),
                (0, 0, {
                    'name': '/',
                    'partner_id': self.customer.id,
                    'account_id': self.receivable.id,
                    'credit': 100,
                }),
            ]
        })

        lines = (move.line_ids | self.move_1.line_ids)\
            .filtered(lambda l: l.account_id == self.receivable)
        lines.reconcile()
        self.env.cr.execute(
            """
            UPDATE account_partial_reconcile SET create_date = %s
            WHERE id = %s
            """, (date, lines.mapped('matched_credit_ids').id))

    def _create_supplier_payment(self, date):
        move = self.env['account.move'].create({
            'name': '/',
            'journal_id': self.bank_journal.id,
            'date': date,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'partner_id': self.supplier.id,
                    'account_id': self.payable.id,
                    'debit': 300,
                }),
                (0, 0, {
                    'name': '/',
                    'account_id': self.bank.id,
                    'credit': 300,
                }),
            ]
        })

        lines = (move.line_ids | self.move_3.line_ids)\
            .filtered(lambda l: l.account_id == self.payable)
        lines.reconcile()
        self.env.cr.execute(
            """
            UPDATE account_partial_reconcile SET create_date = %s
            WHERE id = %s
            """, (date, lines.mapped('matched_credit_ids').id))

    def _create_supplier_payment_us(self, date):
        move = self.env['account.move'].create({
            'name': '/',
            'journal_id': self.us_bank_journal.id,
            'date': date,
            'line_ids': [
                (0, 0, {
                    'name': '/',
                    'partner_id': self.supplier.id,
                    'account_id': self.us_payable.id,
                    'debit': 500,
                    'amount_currency': 350,
                    'currency_id': self.usd.id,
                }),
                (0, 0, {
                    'name': '/',
                    'account_id': self.bank_us.id,
                    'credit': 500,
                    'amount_currency': -350,
                    'currency_id': self.usd.id,
                }),
            ]
        })

        lines = (move.line_ids | self.move_4.line_ids)\
            .filtered(lambda l: l.account_id == self.us_payable)
        lines.reconcile()
        self.env.cr.execute(
            """
            UPDATE account_partial_reconcile SET create_date = %s
            WHERE id in %s
            """, (date, tuple(lines.mapped('matched_credit_ids').ids)))

    def test_payable_not_due(self):
        """Maturity date and payable account."""
        res = (
            self.report_cls.with_context(use_maturity_date=True)
            ._get_partner_move_lines(['payable'], '2017-12-31', 'draft', 30)
        )
        self._check_not_due(res, -700)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, -700)

    def test_payable_0_30(self):
        """Maturity date and payable account."""
        res = (
            self.report_cls.with_context(use_maturity_date=True)
            ._get_partner_move_lines(['payable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, -700)
        self._check_30_60(res, 0)
        self._check_total(res, -700)

    def test_receivable_not_due(self):
        """Maturity date and receivable account."""
        res = (
            self.report_cls.with_context(use_maturity_date=True)
            ._get_partner_move_lines(['receivable'], '2017-12-31', 'draft', 30)
        )
        self._check_not_due(res, 300)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, 300)

    def test_receivable_0_30(self):
        """Maturity date and receivable account."""
        res = (
            self.report_cls.with_context(use_maturity_date=True)
            ._get_partner_move_lines(['receivable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, 300)
        self._check_30_60(res, 0)
        self._check_total(res, 300)

    def test_payable_not_due_with_payment(self):
        """
        Maturity date and payable account.

        On 2017-12-31, the 300$ invoice is paid.
        It is not due because the balance date is before the due date.
        """
        self._create_supplier_payment('2017-12-15')
        res = self.report_cls.with_context(use_maturity_date=True)._get_partner_move_lines(
            ['payable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, -400)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, -400)

    def test_payable_0_30_with_payment(self):
        """
        Maturity date and payable account.

        On 2017-12-31, the 300$ invoice is paid.
        It is in the column 0-30 because the aged balance is
        at the due date of the invoice (2018-01-01).
        """
        self._create_supplier_payment('2017-12-15')
        res = self.report_cls.with_context(use_maturity_date=True)._get_partner_move_lines(
            ['payable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, -400)
        self._check_30_60(res, 0)
        self._check_total(res, -400)

    def test_payable_not_due_before_payment(self):
        """Maturity date and payable account.

        On 2017-12-31, both invoices are still open.
        """
        self._create_supplier_payment('2018-01-15')
        res = self.report_cls.with_context(use_maturity_date=True)._get_partner_move_lines(
            ['payable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, -700)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, -700)

    def test_payable_0_30_before_payment(self):
        """Maturity date and payable account."""
        self._create_supplier_payment('2018-01-15')
        res = self.report_cls.with_context(use_maturity_date=True)._get_partner_move_lines(
            ['payable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, -700)
        self._check_30_60(res, 0)
        self._check_total(res, -700)

    def test_receivable_not_due_with_payment(self):
        """
        Maturity date and receivable account.

        On 2017-12-31, the 100$ invoice is paid.
        It is not due because the balance date is before the due date.
        """
        self._create_customer_payment('2017-12-15')
        res = self.report_cls.with_context(use_maturity_date=True)._get_partner_move_lines(
            ['receivable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, 200)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, 200)

    def test_receivable_0_30_with_payment(self):
        """
        Maturity date and receivable account.

        On 2017-12-31, the 100$ invoice is paid.
        It is in the column 0-30 because the aged balance is
        at the due date of the invoice (2018-01-01).
        """
        self._create_customer_payment('2017-12-15')
        res = self.report_cls.with_context(use_maturity_date=True)._get_partner_move_lines(
            ['receivable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, 200)
        self._check_30_60(res, 0)
        self._check_total(res, 200)

    def test_invoice_date_payable_0_30(self):
        """Invoice date and payable account."""
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['payable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, -700)
        self._check_30_60(res, 0)
        self._check_total(res, -700)

    def test_invoice_date_payable_30_60(self):
        """Invoice date and payable account."""
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['payable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, -700)
        self._check_total(res, -700)

    def test_invoice_date_receivable_0_30(self):
        """Invoice date and receivable account."""
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['receivable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, 300)
        self._check_30_60(res, 0)
        self._check_total(res, 300)

    def test_invoice_date_receivable_30_60(self):
        """Invoice date and receivable account."""
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['receivable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, 300)
        self._check_total(res, 300)

    def test_invoice_date_payable_not_due_with_payment(self):
        """
        Invoice date and payment before the aged balance date.

        300$ paid and 400$ left open
        """
        self._create_supplier_payment('2017-12-15')
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['payable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, -400)
        self._check_30_60(res, 0)
        self._check_total(res, -400)

    def test_invoice_date_payable_0_30_with_payment(self):
        """
        Invoice date and payment before the aged balance date.

        300$ paid and 400$ left open
        """
        self._create_supplier_payment('2017-12-15')
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['payable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, -400)
        self._check_total(res, -400)

    def test_invoice_date_payable_not_due_before_payment(self):
        """
        Invoice date and payment after the aged balance date.

        700$ still open at 2017-12-31.
        """
        self._create_supplier_payment('2018-01-15')
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['payable'], '2017-12-31', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, -700)
        self._check_30_60(res, 0)
        self._check_total(res, -700)

    def test_invoice_date_payable_0_30_before_payment(self):
        """
        Invoice date and payment after the aged balance date.

        700$ still open at 2017-12-31.
        """
        self._create_supplier_payment('2018-01-15')
        res = self.report_cls.with_context(use_maturity_date=False)._get_partner_move_lines(
            ['payable'], '2018-01-01', 'draft', 30)
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, -700)
        self._check_total(res, -700)

    def test_use_account_currency_with_no_account(self):
        """
        Use account currency and no given account.

        The account is mandatory when the aged balance is queried
        in specific currency. No lines are show to the user.
        """
        res = (
            self.report_cls.with_context(use_maturity_date=True, use_account_currency=True)
            ._get_partner_move_lines(['payable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, 0)

    def test_use_account_currency_with_company_currency(self):
        """
        Use account currency and account in company currency.

        When the balance is queried in specific account, only the
        amounts for that account are returned.
        """
        res = (
            self.report_cls.with_context(use_maturity_date=True, use_account_currency=True,
                                         filtered_accounts=self.payable)
            ._get_partner_move_lines(['payable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, -300)
        self._check_30_60(res, 0)
        self._check_total(res, -300)

    def test_use_account_currency_with_foreign_currency(self):
        """Maturity date and amount in foreign currency."""
        res = (
            self.report_cls.with_context(use_maturity_date=True, use_account_currency=True,
                                         filtered_accounts=self.us_payable)
            ._get_partner_move_lines(['payable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, -350)
        self._check_30_60(res, 0)
        self._check_total(res, -350)

    def test_not_use_account_currency_with_foreign_currency(self):
        """
        Maturity date and amount in company currency.

        The amounts will be shown in the currency of the company
        but only for the move lines matching the filtered accounts.
        """
        res = (
            self.report_cls.with_context(use_maturity_date=True, use_account_currency=False,
                                         filtered_accounts=self.us_payable)
            ._get_partner_move_lines(['payable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, -400)
        self._check_30_60(res, 0)
        self._check_total(res, -400)

    def test_use_account_currency_with_invoice_date(self):
        """Invoice date and amount in foreign currency."""
        res = (
            self.report_cls.with_context(use_maturity_date=False, use_account_currency=True,
                                         filtered_accounts=self.us_payable)
            ._get_partner_move_lines(['payable'], '2018-01-01', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, -350)
        self._check_total(res, -350)

    def test_invoice_date_payable_0_30_foreign_currency(self):
        """
        Amount in currency paid after the aged balance date.

        The amount of 350$ is still open on 2017-12-31.
        """
        self._create_supplier_payment_us('2018-01-15')
        res = (
            self.report_cls.with_context(use_maturity_date=False, use_account_currency=True,
                                         filtered_accounts=self.us_payable)
            ._get_partner_move_lines(['payable'], '2017-12-31', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, -350)
        self._check_30_60(res, 0)
        self._check_total(res, -350)

    def test_invoice_date_already_paid_foreign_currency(self):
        """
        Amount in currency paid before the aged balance date.

        The amount of 350$ is paid on 2017-12-31.
        There is nothing left to pay in USD.
        """
        self._create_supplier_payment_us('2017-12-15')
        res = (
            self.report_cls.with_context(use_maturity_date=False, use_account_currency=True,
                                         filtered_accounts=self.us_payable)
            ._get_partner_move_lines(['payable'], '2017-12-31', 'draft', 30)
        )
        self._check_not_due(res, 0)
        self._check_0_30(res, 0)
        self._check_30_60(res, 0)
        self._check_total(res, 0)
