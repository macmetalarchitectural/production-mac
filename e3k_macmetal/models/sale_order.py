# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
  _inherit = "sale.order"

  delivery_route = fields.Selection([
    ('Route1', 'Route 1 - Laurentides, Laval, Lanaudière'),
    ('Route2', 'Route 2 - Estrie, Rive-Sud'),
    ('Route3', 'Route 3 - Montréal'),
    ('Route4', 'Route 4 - Autres')], string='Delivery Route', readonly=True, help='Preferred delivery route.',
    states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]})

  customer_delivery_date = fields.Datetime('Delivery Date', copy=False,
    help="This is the delivery date selected by the customer.")