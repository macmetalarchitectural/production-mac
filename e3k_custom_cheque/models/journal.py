# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountCurrency(models.Model):
    _inherit = "account.journal"

    date_format = fields.Selection([('en_format', 'mm/dd/YYYY'), ('fr_format', 'dd/mm/YYYY')],
                                   string='Checks date format', default='fr_format')
    date_format_str = fields.Char('Format custom', default='dd/mm/YYYY')

    @api.onchange('date_format')
    def onchange_date_format(self):
        if self.date_format == 'en_format':
            self.date_format_str = 'mm/dd/YYYY'
        else:
            self.date_format_str = 'dd/mm/YYYY'

    @api.constrains('date_format_str')
    def _constrains_date_format_str(self):
        for journal in self:
            if 'mm' not in journal.date_format_str or 'dd' not in journal.date_format_str or 'YYYY' not in journal.date_format_str:
                raise ValidationError(_('Please respect the date format example dd/mm/YYYY'))

