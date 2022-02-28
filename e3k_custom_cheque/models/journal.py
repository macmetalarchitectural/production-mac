# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountCurrency(models.Model):
    _inherit = "account.journal"

    date_format = fields.Selection([('en_format', 'mm/dd/YYYY'), ('fr_format', 'dd/mm/YYYY')],
                                   string='Checks date format', default='fr_format')
