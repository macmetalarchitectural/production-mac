# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models

class StockRule(models.Model):
  _inherit = "stock.rule"

  def _make_po_get_domain(self, company_id, values, partner):
    domain = super()._make_po_get_domain(company_id, values, partner)
    return domain + (("block_auto_purchase_order", "=", False),)
