# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # delivery_route = fields.Selection([
    #   ('Route1', 'Livraison MAC'),
    #   ('Route2', 'Livraison GMR'),
    #   ('Route3', 'Livraison Lacroix'),
    #   ('Route4', 'Livraison - Autre'),
    #   ('Route5', 'Pick up'),
    #   ('Route6', 'Target'),], string='Delivery Route', help='Preferred delivery route.',)

    delivery_route_id = fields.Many2one(  # no-check
        'mac.route.config',
        string='Delivery Route',
        help='Preferred delivery route.',
    )
    # states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]})

    customer_delivery_date = fields.Datetime(  # no-check
        'Customer delivery date', copy=False, help="This is the delivery date selected by the customer."
    )

    e3k_division_id = fields.Many2one(  # no-check
        "res.partner",
        string="Division",
        related="partner_id.e3k_division_id",
        store=True,
        readonly=True,
    )
    e3k_follow_up_date = fields.Date(string="Follow-up Date")  # no-check
    e3k_inside_sales_rep_id = fields.Many2one(  # no-check
        "res.users",
        related="partner_id.e3k_inside_sales_rep_id",
        store=True,
        readonly=False,
        string="Inside Sales Rep",
        help="The order desk employee who is responsible for the client account.",
    )
    e3k_maison_mere_id = fields.Many2one(  # no-check
        "res.partner",
        string="Parent Company",
        related="partner_id.e3k_maison_mere_id",
        store=True,
        readonly=True,
    )
    e3k_on_hold = fields.Boolean(  # no-check
        string="On Hold",
        default=False,
        help="The order is on hold when the checkbox is checked.",
    )
    e3k_receipt_date = fields.Datetime(string="Date of Receipt")  # no-check
    e3k_replacement = fields.Boolean(  # no-check
        string="Replacement",
        default=False,
        help="The order is a replacement when the checkbox is checked.",
    )
