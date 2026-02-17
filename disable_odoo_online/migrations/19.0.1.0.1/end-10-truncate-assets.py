import logging

from odoo.upgrade import util

e3k_logger = logging.getLogger(__name__)
E3K_PREFIX_LOG = '----------------------> e3k log : '


def truncate_ir_asset_table(cr):
    try:
        util.parallel_execute(cr, [util.format_query(cr, "TRUNCATE TABLE ir_asset")])
        e3k_logger.warning(E3K_PREFIX_LOG + "Truncate table ir_asset successfully executed")
    except Exception as e:
        e3k_logger.warning(E3K_PREFIX_LOG + f"Failed to truncate table ir_asset: {e}")


def normalize_balance_currency_signs(cr):
    """
    Fix account_move_line data to comply with Odoo v19 native constraint.

    The constraint requires that balance and amount_currency must have the SAME SIGN:
    - Both positive (debit)
    - Both negative (credit)
    - Both zero

    The correction formula: amount_currency = SIGN(balance) * ABS(amount_currency)

    Examples:
    - balance = 100, amount_currency = -50  => amount_currency becomes 50
    - balance = -100, amount_currency = 50  => amount_currency becomes -50
    - balance = 0, amount_currency = 50     => amount_currency becomes 0

    This preserves the absolute value but aligns the sign with balance.
    """
    if not util.module_installed(cr, 'mac_reports'):
        e3k_logger.warning(E3K_PREFIX_LOG + "Starting account_move_line data correction")

        # DATA CORRECTION to comply with Odoo v19 native constraint
        e3k_logger.warning(E3K_PREFIX_LOG + "Searching for lines with inconsistent signs between balance and amount_currency...")
        cr.execute("""
            SELECT COUNT(*)
            FROM account_move_line
            WHERE display_type NOT IN ('line_section', 'line_subsection', 'line_note')
              AND NOT ((balance <= 0 AND amount_currency <= 0) OR (balance >= 0 AND amount_currency >= 0))
        """)
        count = cr.fetchone()[0]
        e3k_logger.warning(E3K_PREFIX_LOG + f"{count} lines with inconsistent signs found")

        if count > 0:
            e3k_logger.warning(E3K_PREFIX_LOG + "Correction: aligning amount_currency sign with balance sign...")
            e3k_logger.warning(E3K_PREFIX_LOG + "Formula: amount_currency = SIGN(balance) * ABS(amount_currency)")
            cr.execute("""
                UPDATE account_move_line
                SET amount_currency = SIGN(balance) * ABS(amount_currency)
                WHERE display_type NOT IN ('line_section', 'line_subsection', 'line_note')
                  AND NOT ((balance <= 0 AND amount_currency <= 0) OR (balance >= 0 AND amount_currency >= 0))
            """)
            e3k_logger.warning(E3K_PREFIX_LOG + f"{count} lines corrected - amount_currency sign aligned with balance")

        e3k_logger.warning(E3K_PREFIX_LOG + "Correction completed - Odoo will automatically recreate the correct constraint")


def migrate(cr, version):

    truncate_ir_asset_table(cr)

    normalize_balance_currency_signs(cr)