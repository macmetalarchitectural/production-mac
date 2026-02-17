# -*- coding: utf-8 -*-
import re

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    print_ordered_qty = fields.Boolean(  # no-check
        string='print ordedred qty', compute="_compute_print_ordered_qty", store=True
    )
    print_delivered_qty = fields.Boolean(  # no-check
        string='print Delivered qty', compute="_compute_print_delivered_qty", store=True
    )
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

    def _compute_print_ordered_qty(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp_key = 'e3k_default_reports.add_ordered_qty_in_report'
        self.print_ordered_qty = icp.get_param(icp_key) or False

    def _compute_print_delivered_qty(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp_key = 'e3k_default_reports.add_qty_delivered_in_report'
        self.print_ordered_qty = icp.get_param(icp_key) or False

    def compute_print_default_code(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp_key = 'e3k_default_reports.add_qty_delivered_in_report'
        return icp.get_param(icp_key) or False

    def compute_add_default_sale_description(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp_key = 'e3k_default_reports.add_default_sale_description'
        return icp.get_param(icp_key) or False

    def compute_add_default_taxes(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp_key = 'e3k_default_reports.add_default_taxes'
        return icp.get_param(icp_key) or False


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def ge_commanded_qty(self):
        qty = 0
        if self.purchase_line_id:
            qty = self.purchase_line_id.product_uom_qty
        else:
            for sale_line in self.sale_line_ids:
                qty += sale_line.product_uom_qty
        return qty

    def ge_commanded_qty_delivered_received(self):
        self.ensure_one()

        if self.purchase_line_id:
            return self.purchase_line_id.qty_received

        return sum(self.sale_line_ids.mapped('qty_delivered'))

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)
        return None

    def get_name_ref_no_desc(self):
        for rec in self:
            if rec.name:
                return rec.name.split('\n')[0]
        return None

    def get_name_no_ref_no_desc(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name).split('\n')[0]
        return None
