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
    'e3k_advanced_payment',
    'auth_totp_password_security'
]

_RENAMED_FIELDS = [
      # helpdesk.ticket
      ("helpdesk.ticket",  "x_studio_amount",                    "e3k_old_amount"),
      ("helpdesk.ticket",  "x_studio_amount_1",                  "e3k_amount"),
      ("helpdesk.ticket",  "x_studio_ticket_product_type",       "e3k_ticket_product_type_id"),
      # product.template
      ("product.template", "x_studio_drawing",                   "e3k_drawing"),
      # res.partner
      ("res.partner",      "x_studio_division",                  "e3k_division_id"),
      ("res.partner",      "x_studio_inside_sales_rep",          "e3k_inside_sales_rep_id"),
      ("res.partner",      "x_studio_maison_mre",                "e3k_maison_mere_id"),
      # sale.order
      ("sale.order",       "x_studio_division",                  "e3k_division_id"),
      ("sale.order",       "x_studio_follow_up_date",            "e3k_follow_up_date"),
      ("sale.order",       "x_studio_inside_sales_rep",          "e3k_inside_sales_rep_id"),
      ("sale.order",       "x_studio_maison_mre",                "e3k_maison_mere_id"),
      ("sale.order",       "x_studio_on_hold",                   "e3k_on_hold"),
      ("sale.order",       "x_studio_receipt_date",              "e3k_receipt_date"),
      ("sale.order",       "x_studio_replacement",               "e3k_replacement"),
      # stock.move
      ("stock.move",       "x_studio_date_field_WyUyd",          "e3k_date_field"),
      # stock.picking
      ("stock.picking",    "x_studio_delivery_on_hold",          "e3k_delivery_on_hold"),
      ("stock.picking",    "x_studio_sales_value",               "e3k_sales_value"),
        # e3k.ticket.product.type
      ("e3k.ticket.product.type",    "x_name",               "name"),
  ]

_RENAME_MODELS = [
    ('x_ticket_product_type','e3k.ticket.product.type')
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

    {
        "operation": "unlink",
        "xmlids": [
            "mac_reports.e3k_report_delivery_document",
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

def set_studio_fields_as_base(cr):
    fields_by_model = {}
    for model, field_name, _ in _RENAMED_FIELDS:
        fields_by_model.setdefault(model, []).append(field_name)

    for model, field_names in fields_by_model.items():
        cr.execute("""
            UPDATE ir_model_fields
            SET state = 'base'
            WHERE model = %s
              AND name = ANY(%s)
              AND state != 'base'
        """, (model, field_names))
        e3k_logger.warning(E3K_PREFIX_LOG + f"Set state='base' for {model}: {field_names} ({cr.rowcount} rows updated)")


def rename_fields(cr):
    for model, old_name, new_name in _RENAMED_FIELDS:
        e3k_logger.warning(E3K_PREFIX_LOG + f"Renaming field {model}.{old_name} to {new_name}")
        util.rename_field(cr, model, old_name, new_name)
        e3k_logger.warning(E3K_PREFIX_LOG + f"Field {model}.{old_name} renamed to {new_name} successfully")


def rename_models(cr):
    for old_name, new_name in _RENAME_MODELS:
        e3k_logger.warning(E3K_PREFIX_LOG + f"Renaming model {old_name} to {new_name}")
        util.rename_model(cr, old_name, new_name)
        e3k_logger.warning(E3K_PREFIX_LOG + f"Model {old_name} renamed to {new_name} successfully")

    # Fix ir.model.data: reassign the external ID of the renamed model so that
    # the CSV (model_e3k_ticket_product_type in e3k_macmetal) resolves correctly.
    cr.execute("""
        UPDATE ir_model_data imd
        SET module = 'e3k_macmetal',
            name   = 'model_e3k_ticket_product_type'
        FROM ir_model im
        WHERE imd.res_id  = im.id
          AND imd.model   = 'ir.model'
          AND im.model    = 'e3k.ticket.product.type'
          AND (imd.module != 'e3k_macmetal' OR imd.name != 'model_e3k_ticket_product_type')
    """)
    e3k_logger.warning(E3K_PREFIX_LOG + f"Fixed ir.model.data external ID for e3k.ticket.product.type ({cr.rowcount} row updated)")

def migrate(cr, version):
    env = util.env(cr)

    rename_models(cr)

    set_studio_fields_as_base(cr)

    rename_fields(cr)

    remove_non_used_modules(cr)

    manage_datas(env, ACTIONS_TO_DO_BEFORE)
