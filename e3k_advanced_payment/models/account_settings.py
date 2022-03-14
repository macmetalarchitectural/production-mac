# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_journal_discount(models.Model):
    _name = 'account.journal.discount'

    company_id = fields.Many2one('res.company', string="Company", required=True)
    journal_discount_client_id = fields.Many2one('account.journal', string="Journal Client Discount")
    journal_discount_supplier_id = fields.Many2one('account.journal', string="Journal Supplier Discount")

    _sql_constraints = [
        ('number_uniq', 'unique(company_id)', "You can't create many lines for the same company!"),
    ]
