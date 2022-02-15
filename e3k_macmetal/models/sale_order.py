# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
  _inherit = "sale.order"

  customer_delivery_date = fields.Datetime('Delivery Date', copy=False,
    help="This is the delivery date selected by the customer.")