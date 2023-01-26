# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.sale.models.account_move import AccountMove as ACM

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # OVERRIDE
        # Recompute 'partner_shipping_id' based on 'partner_id'.
        #addr = self.partner_id.address_get(['delivery'])
        #self.partner_shipping_id = addr and addr.get('delivery')

        res = super(ACM, self)._onchange_partner_id()

        return res
