# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html_keep_url, is_html_empty


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        """
        Computes partner_shipping_id only for orders where it is not already set.

        Restricts parent computation to preserve existing shipping partners.
        """
        orders_to_compute = self.filtered(lambda order: not order.partner_shipping_id)
        if orders_to_compute:
            super(SaleOrder, orders_to_compute)._compute_partner_shipping_id()
