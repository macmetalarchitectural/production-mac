# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
  _inherit = "sale.order"

  # delivery_route = fields.Selection([
  #   ('Route1', 'Livraison MAC'),
  #   ('Route2', 'Livraison GMR'),
  #   ('Route3', 'Livraison Lacroix'),
  #   ('Route4', 'Livraison - Autre'),
  #   ('Route5', 'Pick up'),
  #   ('Route6', 'Target'),], string='Delivery Route', help='Preferred delivery route.',)

  delivery_route_id = fields.Many2one('mac.route.config', string='Delivery Route', help='Preferred delivery route.',)
    # states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]})

  customer_delivery_date = fields.Datetime('Customer delivery date', copy=False,
    help="This is the delivery date selected by the customer.")

