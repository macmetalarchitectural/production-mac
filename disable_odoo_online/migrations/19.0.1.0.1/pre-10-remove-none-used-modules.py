import logging

from odoo.upgrade import util

e3k_logger = logging.getLogger(__name__)
E3K_PREFIX_LOG = '----------------------> e3k log : '


MODULES_TO_REMOVE = [
    'auditlog',
    'mass_editing',
    'ui_color_wasabi',
    'web_custom_label',
    'stock_move_list_partner',
    'sale_order_search_by_client_order_ref',
    'e3k_advanced_payment',
    'password_security',
    'mac_reports',
    'account_invoice_supplier_ref_unique',
]

MODULE_TO_UNINSTALL = [
    # 'e3k_eft',
]


# ACTION_REMOVE_KS_GANTT = [521]

# MENU_TO_DELETE_xml_id = ['project.menu_projects_group_stage', 'project.menu_project_management_my_tasks']
# MODULE_TO_FORCE_UPDATE = ['project']

ACTIONS_TO_DO_BEFORE = [
    # Liste des actions à appliquer sur les enregistrements Odoo.
    # Chaque dictionnaire doit contenir
    # - "operation": le type d'opération à effectuer ("unarchive", "unlink", "reset").
    # - "datas_xmlids" ou "xmlids": liste des identifiants XML des enregistrements cibles.
    # - "records": dictionnaire où la clé est le nom du modèle
    #   et la valeur est la liste des IDs d'enregistrements sur lesquels
    #   appliquer l'opération.
    # {
    #     "operation": "unlink",
    #     "xmlids": [
    #         "e3k_default_reports.res_config_settings_sale_view_form_packaging_info",
    #         "e3k_default_reports.report_delivery_st_baleco",
    #         "l10n_ca_reports.l10n_ca_balance_sheet",
    #     ],
    #     'records': {},
    # },
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
                record.active = True
                e3k_logger.warning(logger_prefix + f"Unarchivé {identifier}")
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


def remove_non_used_modules(cr):
    for module in MODULES_TO_REMOVE:
        try:
            e3k_logger.warning(E3K_PREFIX_LOG + f"Start removing module {module}")
            util.remove_module(cr, module)
            e3k_logger.warning(E3K_PREFIX_LOG + f"Removed module {module}")
        except Exception as e:
            e3k_logger.warning(E3K_PREFIX_LOG + f"Failed to remove module {module}: {e}")

    # for module in MODULE_TO_UNINSTALL:
    #     try:
    #         e3k_logger.warning(E3K_PREFIX_LOG + f"Start uninstalling module {module}")
    #         util.uninstall_module(cr, module)
    #         e3k_logger.warning(E3K_PREFIX_LOG + f" module uninstalled {module}")
    #     except Exception as e:
    #         e3k_logger.warning(E3K_PREFIX_LOG + f"Failed to uninstall  module {module}: {e}")


def migrate(cr, version):
    env = util.env(cr)

    remove_non_used_modules(cr)
