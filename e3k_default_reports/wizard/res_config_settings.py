# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    add_ordered_qty_in_report = fields.Boolean(string="Print Ordered Quantity")  # no-check
    add_qty_delivered_in_report = fields.Boolean(string="Print Delivered Quantity")  # no-check
    add_default_code_report = fields.Boolean(string="Separate column for internal reference?")  # no-check
    add_default_sale_description = fields.Boolean(string="Print Sale description")  # no-check
    add_default_taxes = fields.Boolean(string="Print taxes")  # no-check
    use_sale_order_terms = fields.Boolean(string='Default Terms and Conditions')  # no-check
    sale_order_terms = fields.Text(  # no-check
        related='company_id.sale_order_terms',
        string="Terms and Conditions",
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env['ir.config_parameter'].sudo()
        res.update(
            add_ordered_qty_in_report=icp.get_param('e3k_default_reports.add_ordered_qty_in_report'),
            add_qty_delivered_in_report=icp.get_param('e3k_default_reports.add_qty_delivered_in_report'),
            use_sale_order_terms=icp.get_param('e3k_default_reports.use_sale_order_terms'),
            add_default_code_report=icp.get_param('e3k_default_reports.add_default_code_report'),
            add_default_sale_description=icp.get_param('e3k_default_reports.add_default_sale_description'),
            add_default_taxes=icp.get_param('e3k_default_reports.add_default_taxes'),
        )
        return res

    def set_values(self):
        res = super().set_values()
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param(
            "e3k_default_reports.add_ordered_qty_in_report",
            self.add_ordered_qty_in_report,
        )
        icp.set_param(
            "e3k_default_reports.add_qty_delivered_in_report",
            self.add_qty_delivered_in_report,
        )
        icp.set_param("e3k_default_reports.add_default_code_report", self.add_default_code_report)
        icp.set_param("e3k_default_reports.use_sale_order_terms", self.use_sale_order_terms)
        icp.set_param(
            "e3k_default_reports.add_default_sale_description",
            self.add_default_sale_description,
        )
        icp.set_param("e3k_default_reports.add_default_taxes", self.add_default_taxes)
        return res
