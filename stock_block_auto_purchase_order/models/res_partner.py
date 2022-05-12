# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields

BLOCK_AUTO_HELP = (
  "When checked, this field prevents products from being automatically added to the PO by the system."
)

UNIQUE_PO_HELP = (
  "When checked, this field forces items to be added to a default supplier."
)

class ResPartner(models.Model):
  _inherit = "res.partner"

  block_auto_purchase_order = fields.Boolean(
    string="Block Automatic Product Add",
    default=False,
    help=BLOCK_AUTO_HELP,
  )

  unique_purchase_order = fields.Boolean(
    string="Unique Purchase Order",
    default=True,
    help=UNIQUE_PO_HELP,
  )

  @api.onchange("block_auto_purchase_order")
  def onchange_block_auto_purchase_order(self):
    if self.unique_purchase_order and self.block_auto_purchase_order:
      self.unique_purchase_order = False

  @api.onchange("unique_purchase_order")
  def onchange_unique_purchase_order(self):
    if self.block_auto_purchase_order and self.unique_purchase_order:
      self.block_auto_purchase_order = False
