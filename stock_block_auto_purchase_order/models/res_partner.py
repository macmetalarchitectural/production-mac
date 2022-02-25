# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields

BLOCK_AUTO_HELP = (
  "When checked, this field prevents products from being automatically added to the PO by the system."
)

class ResPartner(models.Model):
  _inherit = "res.partner"

  block_auto_purchase_order = fields.Boolean(
    string="Block Automatic Product Add",
    default=False,
    help=BLOCK_AUTO_HELP,
  )
