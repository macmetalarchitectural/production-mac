# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    invoice_print_report = fields.Selection(  # no-check
        selection=[
            ('standard', 'Detailed'),
            ('summary', 'Summary'),
            ('detail', 'Semi-detailed'),
        ],
        help='Default print invoice',
        default='detail',
    )
    invoice_text = fields.Html('Invoice text')  # no-check
