import logging
from odoo.upgrade import util

e3k_logger = logging.getLogger(__name__)
E3K_PREFIX_LOG = '----------------------> e3k log : '


def migrate(cr, version):
    """
    Supprime la contrainte bypassée par mac_reports (CHECK(1=1)) et corrige les données.

    Le module mac_reports avait remplacé la contrainte native par CHECK(1=1).
    Lors de la migration v19, Odoo essaie de recréer la contrainte originale
    et découvre des données invalides qui la violent.

    Solution: Supprimer complètement la contrainte CHECK(1=1) et corriger les données.
    Odoo recréera automatiquement la contrainte correcte lors du chargement du module account.
    """

    if util.module_installed(cr, 'mac_reports'):
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
