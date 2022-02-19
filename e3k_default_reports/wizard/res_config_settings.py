# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    add_ordered_qty_in_report = fields.Boolean(string="Print Ordered Quantity")
    add_qty_delivered_in_report = fields.Boolean(string="Print Delivered Quantity")
    add_default_code_report = fields.Boolean(string="Print Internal reference")
    add_default_sale_description = fields.Boolean(string="Print Sale description")

    use_sale_order_terms = fields.Boolean(
        string='Default Terms and Conditions')

    sale_order_terms = fields.Text(related='company_id.sale_order_terms', string="Terms and Conditions", readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            add_ordered_qty_in_report=params.get_param('e3k_default_reports.add_ordered_qty_in_report'),
            add_qty_delivered_in_report=params.get_param('e3k_default_reports.add_qty_delivered_in_report'),
            use_sale_order_terms=params.get_param('e3k_default_reports.use_sale_order_terms'),
            add_default_code_report=params.get_param('e3k_default_reports.add_default_code_report'),
            add_default_sale_description=params.get_param('e3k_default_reports.add_default_sale_description'),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("e3k_default_reports.add_ordered_qty_in_report",
                                                         self.add_ordered_qty_in_report)
        self.env['ir.config_parameter'].sudo().set_param("e3k_default_reports.add_qty_delivered_in_report",
                                                         self.add_qty_delivered_in_report)
        self.env['ir.config_parameter'].sudo().set_param("e3k_default_reports.add_default_code_report",
                                                         self.add_default_code_report)
        self.env['ir.config_parameter'].sudo().set_param("e3k_default_reports.use_sale_order_terms",
                                                         self.use_sale_order_terms)
        self.env['ir.config_parameter'].sudo().set_param("e3k_default_reports.add_default_sale_description",
                                                         self.add_default_sale_description)
