# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.sale.models.account_move import AccountMove as ACM

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        """
        Intentionally disabled: delivery address is never auto-filled when a partner
        is selected on an invoice. The user must choose it manually.
        """
