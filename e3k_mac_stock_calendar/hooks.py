from odoo import api, SUPERUSER_ID

from . import models

def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["stock.picking"].search([])._copy_val_from_x_delivery_pickup()

    view_ids_to_delete = [1975, 1976]
    env["ir.ui.view"].browse(view_ids_to_delete).unlink()