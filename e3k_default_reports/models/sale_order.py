# -*- coding: utf-8 -*-
import re

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'info.block.report.mixin']

    @api.model
    def _default_sale_note_terms(self):
        icp = self.env['ir.config_parameter'].sudo()
        if icp.get_param('e3k_default_reports.use_sale_order_terms'):
            return self.env.company.sale_order_terms or ''

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
    invoice_text = fields.Html(string='Invoice text', translate=True)  # no-check
    sale_note_termes = fields.Text(  # no-check
        'Sales Terms and conditions',
        default=lambda self: self._default_sale_note_terms(),
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.invoice_print_report = self.partner_id.invoice_print_report

    @api.model
    def _get_icp_value(self, icp_key):
        return self.env['ir.config_parameter'].sudo().get_param(icp_key) or False

    def compute_print_default_code(self):
        return self._get_icp_value('e3k_default_reports.add_default_code_report')

    def compute_print_default_sale_description(self):
        return self._get_icp_value('e3k_default_reports.add_default_sale_description')

    def compute_add_default_taxes(self):
        return self._get_icp_value('e3k_default_reports.add_default_taxes')

    def _prepare_invoice(self):
        """
            Override
            Add new value in dict of invoice value
        :return: dictionary of value
        """
        res = super()._prepare_invoice()
        res.update(
            {
                'invoice_print_report': self.invoice_print_report,
                'invoice_text': self.invoice_text,
            }
        )
        return res

    def information_block_to_display(self):
        return {
            'client_order_ref': {
                'label': _('Customer reference'),
                'value': self.client_order_ref or False,
                'type': 'string',
            },
            'date_order': {'label': _('Order Date'), 'value': self.date_order or False, 'type': 'date'},
            'commitment_date': {'label': _('Commitment date'), 'value': self.commitment_date or False, 'type': 'date'},
            'user_id': {'label': _('Salesperson'), 'value': self.user_id.name or False, 'type': 'string'},
            'payment_term_id': {
                'label': _('Payment Terms'),
                'value': self.payment_term_id.name or False,
                'type': 'string',
            },
            'partner_id': {
                'label': _('Shipped via'),
                'value': self.partner_id.property_delivery_carrier_id.name or False,
                'type': 'string',
            },
            'validity_date': {'label': _('Expiration'), 'value': self.validity_date or False, 'type': 'date'},
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)
        return None

    def get_sale_order_line_multiline_description_sale(self, product):
        return product.name

    def get_name_ref_no_desc(self):
        for rec in self:
            if rec.name:
                return rec.name.split('\n')[0]
        return None
