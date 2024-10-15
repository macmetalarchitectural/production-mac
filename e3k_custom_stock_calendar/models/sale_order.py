# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # delivery_route = fields.Selection([('Route1', 'Pickup'),
    #                                    ('Route2', 'Delivery'),
    #                                    ('Route3', 'Pickup'),
    #                                    ('Route4', 'Delivery'),
    #                                    ('Route5', 'Pickup'),
    #                                    ('Route6', 'Delivery'),
    #                                    ], string='Delivery Route', default='delivery', required=True)
    #
    # @api.model
    # def _action_get_value_from_x_delivery_route(self):
    #     for rec in self.search([]):
    #         if hasattr(rec, 'x_delivery_route'):
    #             rec.delivery_route = rec.x_delivery_route
