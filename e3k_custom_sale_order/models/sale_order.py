# -*- coding: utf-8 -*-

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        """
               Intentionally disabled: delivery address is never auto-filled when a partner
               is selected on an invoice. The user must choose it manually.
           """
