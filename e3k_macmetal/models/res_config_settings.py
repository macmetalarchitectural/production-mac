# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    delivery_terms = fields.Html(  # no-check
        string="Default Delivery Terms & Conditions",
        related="company_id.delivery_terms",
        readonly=False,
    )
    use_delivery_terms = fields.Boolean(  # no-check
        string="Delivery Default Terms & Conditions",
        config_parameter="e3k_macmetal.use_delivery_terms",
        default=False,
    )
    padding_delivery_days = fields.Integer(  # no-check
        string="Padding Delivery Days",
        related="company_id.padding_delivery_days",
        readonly=False,
        help="Amount of days",
    )
