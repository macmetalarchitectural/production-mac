# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_sale_order_line_multiline_description_sale(self, product):
        description = super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
        if product.description_sale:
            result = product.display_name + ' ' + product.description_sale
        else:
            result = product.display_name

        return result
