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
    {
        "operation": "unlink",
        "xmlids": [
            "studio_customization.odoo_studio_res_part_53e160e5-7142-4672-a104-1ff718a33dda",
            "studio_customization.odoo_studio_sale_ord_155972b3-8324-4337-b41c-64d309b806d6",
            "studio_customization.odoo_studio_sale_ord_6885aa07-95db-45d2-940d-6b404294b486",
            "studio_customization.odoo_studio_sale_ord_ee0c6151-f94a-483e-9c80-0105c1441f62",
            "studio_customization.odoo_studio_helpdesk_80283aa9-d13f-4317-be2e-a7de59c1cf86",
            "studio_customization.odoo_studio_product__ac58e971-6a32-47a5-9ff8-637df088ef28",
            "studio_customization.odoo_studio_purchase_a0749a94-7f1b-4fd4-9471-d5ded433ea96",
            "studio_customization.odoo_studio_res_part_6c52af64-9ba0-4499-9931-b22a739f56eb",
            "studio_customization.odoo_studio_stock_mo_c855b356-05ad-42e5-a649-a6ba1543760c",
            "studio_customization.odoo_studio_stock_pi_b768ae15-bd79-449f-b41a-f5ed340eaa04",
            "studio_customization.odoo_studio_stock_pi_75276b15-12a9-473c-8a1d-fd4eafe68cf7",
            "studio_customization.odoo_studio_stock_pi_4a4c824c-32ed-4f06-b115-e13d89dd853c",
        ],
        'records': {},
    },
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
  ]

_RENAME_MODELS = [
    ('x_ticket_product_type','e3k.ticket.product.type')
]

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



def migrate(cr, version):
    env = util.env(cr)

    rename_models(cr)

    rename_fields(cr)

    truncate_ir_asset_table(cr)

    manage_datas(env, ACTIONS_TO_DO)
