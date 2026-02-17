# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_print_report = fields.Selection(  # no-check
        selection=[
            ('standard', 'Standard'),
            ('summary', 'Summary'),
            ('detail', 'Semi-detailed'),
        ],
        help='Default print invoice',
        default='standard',
        required=True,
    )

    sale_order_template_id = fields.Many2one('sale.order.template', string='Default Sale Order Template')  # no-check

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        template = self.sale_order_template_id
        self.invoice_print_report = template.invoice_print_report or 'standard'
