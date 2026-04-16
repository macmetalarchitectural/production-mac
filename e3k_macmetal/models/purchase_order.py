# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_sale_orders(self):
        return super()._get_sale_orders() | self.reference_ids.move_ids.picking_id.sale_id
