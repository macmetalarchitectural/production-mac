import logging

from odoo.upgrade import util

e3k_logger = logging.getLogger(__name__)
E3K_PREFIX_LOG = '----------------------> e3k log : '

MODULE_TO_FORCE_INSTALL = ['E3K_default_stages']

ACTIONS_TO_DO_AFTER = [
    # Liste des actions à appliquer sur les enregistrements Odoo.
    # Chaque dictionnaire doit contenir
    # - "operation": le type d'opération à effectuer ("unarchive", "unlink", "reset").
    # - "datas_xmlids" ou "xmlids": liste des identifiants XML des enregistrements cibles.
    # - "records": dictionnaire où la clé est le nom du modèle
    #   et la valeur est la liste des IDs d'enregistrements sur lesquels
    #   appliquer l'opération.
    {
        "operation": "unlink",
        "xmlids": [
            "project.open_view_project_all_group_stage_kanban_view",
            "project.open_view_project_all_group_stage_tree_view",
        ],
        'records': {'ir.actions.act_window': [521, 529]},
    },
    {
        "operation": "unarchive",
        "datas_xmlids": [
            # views
            'e3k_vd_account_custom.view_move_form_inherit_vd_account_custom',
            'e3k_vd_account_custom.view_in_invoice_tree_inherit_vd_account_custom',
            # menue
            'purchase.purchase_report'
            # reports
            'e3k_default_reports.report_sale_e3k',
            'e3k_vd_project_reporting.report_purchaseorder_document_inherit_date_expected'
            'e3k_purchase_lines_committed.report_purchaseorder_document_inherit_',
            'e3k_default_reports.res_config_settings_account_view_form_add_print_config',
            'e3k_vd_project_reporting.sale_order_report_inherit',
        ],
        'records': {'ir.ui.view': []},
    },
    # {
    #     "operation": "unlink",
    #     "xmlids": [
    #         # reports
    #         "e3k_default_reports.report_delivery_st_baleco",
    #         "l10n_ca_reports.l10n_ca_balance_sheet",
    #     ],
    #     'records': {
    #         'ir.ui.view': []
    #         # Dictionnaire: clé = nom du modèle, valeur = liste d'IDs
    #         # d'enregistrements du modèle sur lesquels appliquer l'opération
    #     },
    # },
    # {
    #     "operation": "reset",
    #     "xmlids": [
    #         # reports
    #         "stock.report_delivery_document"
    #     ],
    #     'records': {'ir.ui.view': []},
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
                record.write({"active": True})
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


def _install_module(
    cr,
):
    for module in MODULE_TO_FORCE_INSTALL:
        try:
            util.force_install_module(cr, module)
            e3k_logger.warning(E3K_PREFIX_LOG + ("Install module %s" % module))
        except Exception:
            e3k_logger.error(E3K_PREFIX_LOG + ("Failed to install module %s" % module))


def truncate_ir_asset_table(cr):
    try:
        util.parallel_execute(cr, [util.format_query(cr, "TRUNCATE TABLE ir_asset")])
        e3k_logger.warning(E3K_PREFIX_LOG + "Truncate table ir_asset successfully executed")
    except Exception as e:
        e3k_logger.warning(E3K_PREFIX_LOG + f"Failed to truncate table ir_asset: {e}")


def migrate(cr, version):
    env = util.env(cr)

    truncate_ir_asset_table(cr)

    _install_module(cr)

    manage_datas(env, ACTIONS_TO_DO_AFTER)
