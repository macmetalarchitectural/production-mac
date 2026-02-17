# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountCurrency(models.Model):
    _inherit = "account.journal"

    date_format = fields.Selection(  # no-check
        [  # no-check
            ('en_format', 'mm/dd/YYYY'),
            ('fr_format', 'dd/mm/YYYY'),
            ('format_3', 'YYYY/mm/dd'),
        ],
        string='Checks date format',
        default='fr_format',
    )
    date_format_str = fields.Char('Format custom', default='dd/mm/YYYY')  # no-check

    @api.onchange('date_format')
    def _onchange_date_format(self):
        if self.date_format == 'en_format':
            self.date_format_str = 'mm/dd/YYYY'
        elif self.date_format == 'format_3':
            self.date_format_str = 'YYYY/mm/dd'
        else:
            self.date_format_str = 'dd/mm/YYYY'

    @api.constrains('date_format_str')
    def _constrains_date_format_str(self):
        for journal in self:
            if all(part in journal.date_format_str for part in ('mm', 'dd', 'YYYY')):
                continue

            raise ValidationError(_('Please respect the date format example dd/mm/YYYY'))
