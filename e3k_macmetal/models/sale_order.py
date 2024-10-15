# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
  _inherit = "sale.order"

  delivery_route = fields.Selection([
    ('Route1', 'Livraison MAC'),
    ('Route2', 'Livraison GMR'),
    ('Route3', 'Livraison Dumais'),
    ('Route4', 'Livraison - Autre'),
    ('Route5', 'Pick up'),
    ('Route6', 'Target'),], string='Delivery Route', help='Preferred delivery route.',)
    # states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]})

  customer_delivery_date = fields.Datetime('Delivery Date', copy=False,
    help="This is the delivery date selected by the customer.")

  @api.model
  def _action_get_value_from_x_delivery_route(self):
    for rec in self.search([]):
      if hasattr(rec, 'x_delivery_route'):
        rec.delivery_route = rec.x_delivery_route
