# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import itertools
from datetime import timedelta, date
from collections import defaultdict
from odoo import fields
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.account.models.account_move import AccountMoveLine
from odoo.addons.account.models.account_account import AccountAccount
from odoo.api import Environment
from odoo.tools import float_is_zero
from typing import List, Iterable, Optional, Tuple, Mapping


def get_aged_partner_balance_periods(report_date_str: str) -> List[dict]:
    """Get the periods to display in the aged partner balance.

    :param report_date_str: the date of the report.
    """
    report_date = fields.Date.from_string(report_date_str)
    return [
        {
            'name': '1 - 30',
            'stop': report_date,
            'start': report_date - timedelta(30),
        },
        {
            'name': '31 - 60',
            'stop': report_date - timedelta(31),
            'start': report_date - timedelta(60),
        },
        {
            'name': '61 - 90',
            'stop': report_date - timedelta(61),
            'start': report_date - timedelta(90),
        },
        {
            'name': '91 - 120',
            'stop': report_date - timedelta(91),
            'start': report_date - timedelta(120),
        },
        {
            'name': '+120',
            'stop': report_date - timedelta(121),
            'start': False,
        },
    ]


def get_move_lines_reconciled_after_date(env: Environment, date_: str) -> AccountMoveLine:
    """Get the account move lines reconciled after the given date.

    :param env: the Odoo environment.
    :param date_: the date of the report.
    """
    env.cr.execute("""
        SELECT rec.debit_move_id, rec.credit_move_id
        FROM account_partial_reconcile rec
        JOIN account_move_line debit ON rec.debit_move_id = debit.id
        JOIN account_move_line credit ON rec.credit_move_id = credit.id
        WHERE debit.date > %s OR credit.date > %s
    """, (date_, date_))
    move_lines_ids = list(itertools.chain(*env.cr.fetchall()))
    return env['account.move.line'].browse(move_lines_ids)


def get_partners_with_unreconciled_moves_at_date(
        env: Environment, date_: str, accounts: AccountAccount,
        move_states: Iterable[str]) -> Partner:
    """Get the partners with unreconciled moves at the given date.

    :param env: the Odoo environment.
    :param date_: the date of the report.
    :param accounts: the filtered accounts.
    :param move_states: a list of account move states to filter.
    """
    query = """
        SELECT l.partner_id
        FROM account_move_line l
        JOIN account_move am ON l.move_id = am.id
        JOIN account_account aa ON l.account_id = aa.id
        WHERE am.state IN %s
        AND aa.id IN %s
        AND (l.reconciled IS FALSE OR l.id IN %s)
        AND (l.date <= %s)
        AND l.company_id = %s
        AND l.partner_id IS NOT NULL
    """
    env.cr.execute(query, (
        tuple(move_states),
        tuple(accounts.ids) or (0, ),
        tuple(get_move_lines_reconciled_after_date(env, date_).ids) or (0, ),
        date_,
        env.user.company_id.id,
    ))
    partner_ids = list({r[0] for r in env.cr.fetchall()})
    return env['res.partner'].browse(partner_ids)


def get_undue_move_lines(
        env: Environment, date_: str, accounts: AccountAccount,
        move_states: Iterable[str]) -> AccountMoveLine:
    """Get all undue account move lines at the given date.

    :param env: the Odoo environment.
    :param date_: the date of the report.
    :param accounts: the filtered accounts.
    :param move_states: a list of account move states to filter.
    """
    query = """
        SELECT l.id
        FROM account_move_line l
        JOIN account_move am ON l.move_id = am.id
        JOIN account_account aa ON l.account_id = aa.id
        WHERE am.state IN %s
        AND aa.id IN %s
        AND COALESCE(l.date_maturity, l.date) > %s
        AND l.date <= %s
        AND l.company_id = %s
        AND l.partner_id IS NOT NULL
    """
    env.cr.execute(query, (
        tuple(move_states),
        tuple(accounts.ids) or (0, ),
        date_,
        date_,
        env.user.company_id.id,
    ))
    move_lines_ids = list({r[0] for r in env.cr.fetchall()})
    return env['account.move.line'].browse(move_lines_ids)


def get_move_line_amount_at_date(
        move_line: AccountMoveLine, date_: str, use_account_currency: bool) -> float:
    """Get the due amount of a move line at a given date.

    :param move_line: the move line for which to find the due amount.
    :param date_: the date at which to get the amount.
    :param use_account_currency: whether to get the amount in local or foreign currency.
    """
    amount_field = 'amount_currency' if use_account_currency else 'balance'
    reconcile_amount_field = 'amount_currency' if use_account_currency else 'amount'

    line_amount = move_line[amount_field]

    line_amount += sum(
        l[reconcile_amount_field] for l in move_line.matched_debit_ids if l.max_date <= date_
    )

    line_amount -= sum(
        l[reconcile_amount_field] for l in move_line.matched_credit_ids if l.max_date <= date_
    )

    return line_amount


def move_lines_due_in_period(
        env: Environment, date_from: Optional[date], date_to: Optional[date],
        accounts: AccountAccount, use_maturity_date: bool,
        move_states: Iterable[str]) -> AccountMoveLine:
    """Get all move lines due in a given period.

    :param env: the Odoo environment.
    :param date_from: the lower period boundary.
    :param date_to: the upper period boundary.
    :param accounts: the filtered accounts.
    :param use_maturity_date: whether to use the maturity date if available.

        Note that Payment move lines have no maturity date. Therefore, the
        column `date` is used if `date_maturity` is not filled.

    :param move_states: a list of account move states to filter.
    """
    date_expression = 'COALESCE(l.date_maturity, l.date)' if use_maturity_date else 'l.date'

    args = (
        tuple(move_states),
        tuple(accounts.ids) or (0, ),
        env.user.company_id.id,
    )

    date_from_str = fields.Date.to_string(date_from) if date_from else None
    date_to_str = fields.Date.to_string(date_to) if date_to else None

    if date_from and date_to:
        args += (date_from_str, date_to_str)
        dates_query = '({} BETWEEN %s AND %s)'.format(date_expression)
    elif date_from:
        args += (date_from_str, )
        dates_query = '({} >= %s)'.format(date_expression)
    else:
        args += (date_to_str, )
        dates_query = '({} <= %s)'.format(date_expression)

    query = """
        SELECT l.id
        FROM account_move_line l
        JOIN account_move am ON l.move_id = am.id
        JOIN account_account aa ON l.account_id = aa.id
        WHERE am.state IN %s
        AND aa.id IN %s
        AND l.company_id = %s
        AND """ + dates_query

    env.cr.execute(query, args)

    move_lines_ids = list({r[0] for r in env.cr.fetchall()})
    return env['account.move.line'].browse(move_lines_ids)


def get_move_lines_per_period(
        env: Environment, date_: str, accounts: AccountAccount,
        use_maturity_date: bool, move_states: Iterable[str]) -> List[AccountMoveLine]:
    """Get all due account move lines grouped by period.

    The returned value is a list of account move line recordsets.

    The first recordset contains the move lines from 1 to 30 days.
    The second recordset contains the move lines from 31 to 60 days.
    ...
    The last recordset contains the move lines exceeding 120 days.

    :param env: the Odoo environment.
    :param date_: the report date.
    :param accounts: the filtered accounts.
    :param use_maturity_date: whether to use the maturity date if available.
    :param move_states: a list of account move states to filter.
    """
    return [
        move_lines_due_in_period(
            env, period['start'], period['stop'], accounts, use_maturity_date, move_states)
        for period in get_aged_partner_balance_periods(date_)
    ]


def is_not_null_amount(env: Environment, amount: float) -> bool:
    """Return True if the given amount is not null, False otherwise."""
    return not float_is_zero(amount, precision_rounding=env.user.company_id.currency_id.rounding)


def get_aged_partner_balance_data(
    env: Environment,
    date_from: str,
    use_maturity_date: bool,
    use_account_currency: bool,
    accounts: AccountAccount,
    move_states: Iterable[str],
) -> Tuple[List[dict], List[float], Mapping[int, List[dict]]]:
    """Get the data to display in the aged partner balance report.

    This function replaces the method _get_partner_move_lines of the aged balance report found at
    odoo/addons/account/report/account_aged_partner_balance.py

    This adds the 2 options use_maturity_date and use_account_currency.

    :param env: the odoo environment
    :param date_from: the date from which to display the aged balance
    :param use_maturity_date: whether to use the maturity date as basis for the aged balance
    :param accounts: the accounts for which to display the aged balance
    :param move_states: the states of account moves to include (['posted'] or ['draft', 'posted'])
    :return: the aged balance data
    """
    move_lines_per_partner_id = defaultdict(list)

    undue_amounts = defaultdict(float)
    undue_move_lines = (
        get_undue_move_lines(env, date_from, accounts, move_states) if use_maturity_date else []
    )

    for line in undue_move_lines:
        line_due_amount = get_move_line_amount_at_date(line, date_from, use_account_currency)

        if not env.user.company_id.currency_id.is_zero(line_due_amount):
            undue_amounts[line.partner_id] += line_due_amount
            move_lines_per_partner_id[line.partner_id.id].append(
                {'line': line, 'amount': line_due_amount, 'period': 6})

    period_totals = []
    history = get_move_lines_per_period(env, date_from, accounts, use_maturity_date, move_states)

    for i, move_lines in enumerate(history):
        total_per_partner = defaultdict(float)
        period_totals.append(total_per_partner)

        for line in move_lines:
            line_due_amount = get_move_line_amount_at_date(line, date_from, use_account_currency)

            if is_not_null_amount(env, line_due_amount):
                total_per_partner[line.partner_id] += line_due_amount
                move_lines_per_partner_id[line.partner_id.id].append({
                    'line': line,
                    'amount': line_due_amount,
                    'period': 6 - i - 1,
                })

    details_per_partner = []
    partners = get_partners_with_unreconciled_moves_at_date(env, date_from, accounts, move_states)
    for partner in partners:
        values = {
            'partner_id': partner.id,
            'name': partner.display_name,
            'trust': partner.trust,
            'direction': undue_amounts.get(partner, 0),
            '0': period_totals[4].get(partner, 0),
            '1': period_totals[3].get(partner, 0),
            '2': period_totals[2].get(partner, 0),
            '3': period_totals[1].get(partner, 0),
            '4': period_totals[0].get(partner, 0),
        }
        values['total'] = (
            values['direction'] +
            values['0'] +
            values['1'] +
            values['2'] +
            values['3'] +
            values['4']
        )
        at_least_one_amount = (
            is_not_null_amount(env, values['direction']) or
            is_not_null_amount(env, values['0']) or
            is_not_null_amount(env, values['1']) or
            is_not_null_amount(env, values['2']) or
            is_not_null_amount(env, values['3']) or
            is_not_null_amount(env, values['4'])
        )
        if at_least_one_amount:
            details_per_partner.append(values)

    totals = [
        sum(period_totals[i].get(p, 0) for p in partners)
        for i in [4, 3, 2, 1, 0]
    ]

    undue_total = sum(undue_amounts.get(p, 0) for p in partners)
    global_total = sum(totals) + undue_total

    totals.append(global_total)
    totals.append(undue_total)

    return details_per_partner, totals, move_lines_per_partner_id
