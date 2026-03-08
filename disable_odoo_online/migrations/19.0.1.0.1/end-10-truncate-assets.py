import logging

from odoo.upgrade import util

e3k_logger = logging.getLogger(__name__)
E3K_PREFIX_LOG = '----------------------> e3k log : '

ACTIONS_TO_DO = [
    # Liste des actions à appliquer sur les enregistrements Odoo.
    # Chaque dictionnaire doit contenir
    # - "operation": le type d'opération à effectuer ("unarchive", "unlink", "reset").
    # - "datas_xmlids" ou "xmlids": liste des identifiants XML des enregistrements cibles.
    # - "records": dictionnaire où la clé est le nom du modèle
    #   et la valeur est la liste des IDs d'enregistrements sur lesquels
    #   appliquer l'opération.
    {
        "operation": "unarchive",
        "xmlids": [
            "e3k_default_reports.res_config_settings_account_view_form_add_print_config",
            "e3k_default_reports.res_config_settings_sale_view_form_add_sale_terms",
            "e3k_default_reports.report_sale_e3k",
            "e3k_custom_cheque.cheque_report_payment_receipt_document_inherit",
            "e3k_notifications_management.res_config_settings_view_form_mail_inherit",
            "password_security.res_config_settings_view_form",
            "e3k_macmetal.res_config_settings_view_form",
            "mac_reports.report_sale_e3k_mac",
            "mac_reports.report_invoice_mac",
            "mac_reports.report_picking_mac",
            "e3k_mac_stock_calendar.e3k_view_picking_internal_search",
            "e3k_mac_contact_customisation.l10n_ca_res_partner_form_inherit_ca",
            "website.footer_language_selector_no_text",
        ],
        'records': {},
    },
]

def _apply_operation(record, op, identifier, logger_prefix):
    """
    Applique une opération spécifique sur un enregistrement Odoo.

    Cette fonction prend un enregistrement Odoo et effectue l'opération demandée parmi :
    - "unarchive" : réactive l'enregistrement s'il possède l'attribut `active`.
    - "unlink" : supprime l'enregistrement de la base de données.
    - "reset" : réinitialise l'enregistrement via la méthode `reset_arch("hard")`.

    Args:
        record: Enregistrement Odoo cible de l'opération.
        op (str): Type d'opération à appliquer ("unarchive", "unlink", "reset").
        identifier (str): Identifiant ou description de l'enregistrement pour le log.
        logger_prefix (str): Préfixe à ajouter aux messages de log.

    Exceptions:
        Toute exception survenue lors de l'opération est interceptée et loggée en warning.
    """
    try:
        if op == "unarchive":
            if hasattr(record, "active"):
                record.write({'active': True})
                e3k_logger.warning(logger_prefix + f"Désarchivé {identifier}")
        elif op == "unlink":
            record.unlink()
            e3k_logger.warning(logger_prefix + f"Supprimé {identifier}")
        elif op == "reset":
            record.reset_arch("hard")
            e3k_logger.warning(logger_prefix + f"Réinitialisé {identifier}")
    except Exception as e:
        e3k_logger.warning(logger_prefix + f"Erreur sur {identifier}: {e}")

def manage_datas(env, ACTIONS):
    """
    Applique les actions définies dans ACTIONS sur les enregistrements Odoo.
    Args:
        env: Odoo environment object.
    """
    for action in ACTIONS:
        op = action.get("operation")
        xmlids = action.get("datas_xmlids") or action.get("xmlids") or []
        records = action.get("records", {})

        # Appliquer l'opération sur les xmlids
        for xmlid in xmlids:
            try:
                record = env.ref(xmlid, raise_if_not_found=False)
            except Exception:
                record = None
            if not record:
                e3k_logger.warning(E3K_PREFIX_LOG + f"xmlid '{xmlid}' non trouvé.")
                continue
            _apply_operation(record, op, xmlid, E3K_PREFIX_LOG)

        # Appliquer l'opération sur les records par modèle
        for model, ids in records.items():
            model_obj = env[model]
            for rec_id in ids:
                rec = model_obj.browse(rec_id)
                if not rec.exists():
                    e3k_logger.warning(E3K_PREFIX_LOG + f"ID {rec_id} non trouvé dans {model}")
                    continue
                _apply_operation(rec, op, f"{model} {rec_id}", E3K_PREFIX_LOG)


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
    env = util.env(cr)
    truncate_ir_asset_table(cr)

    normalize_balance_currency_signs(cr)

    manage_datas(env, ACTIONS_TO_DO)