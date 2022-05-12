# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields

class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        if partner.block_auto_purchase_order:
            domain = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
            domain += (('block_auto_purchase_order', '=', True),)
            domain += (('unique_purchase_order', '=', False),)
            if 'move_dest_ids' in values and values['move_dest_ids']:
                # Trick to have uniq domain per line to force split
                domain += (('notes', '=', str(values['move_dest_ids'])),)
        else:
            if partner.unique_purchase_order:
                partner = self.env['res.partner'].search([('id', '=', 108)])
                domain = super(StockRule, self)._make_po_get_domain(company_id, values, partner)
                domain += (('unique_purchase_order', '=', True),)

            domain += (('block_auto_purchase_order', '=', False),)

        return domain
