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


def drop_check_amount_currency_balance_sign(cr):
    if not util.module_installed(cr, 'mac_reports'):
        e3k_logger.warning(E3K_PREFIX_LOG + "Début de la correction des contraintes account_move_line")

        # Supprimer la contrainte bypassée (CHECK(1=1)) laissée par mac_reports
        cr.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conname = 'account_move_line_check_amount_currency_balance_sign'
              AND conrelid = 'account_move_line'::regclass
        """)

        constraint = cr.fetchone()

        if constraint:
            conname, definition = constraint
            e3k_logger.warning(E3K_PREFIX_LOG + f"Contrainte trouvée: {conname} = {definition}")
            e3k_logger.warning(E3K_PREFIX_LOG + "Suppression de la contrainte bypassée par mac_reports")
            cr.execute("""
                ALTER TABLE account_move_line
                DROP CONSTRAINT account_move_line_check_amount_currency_balance_sign
            """)
        else:
            e3k_logger.warning(E3K_PREFIX_LOG + "Aucune contrainte existante trouvée")


        e3k_logger.warning(E3K_PREFIX_LOG + "Fin - Odoo recréera automatiquement la contrainte correcte")


def migrate(cr, version):

    truncate_ir_asset_table(cr)

    drop_check_amount_currency_balance_sign(cr)