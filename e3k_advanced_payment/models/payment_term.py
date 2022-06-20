# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    payment_discount_percent = fields.Float(string='Percent Discount')
    number_discount_days = fields.Integer(string='Number of days to get discount')
    product_category_ids = fields.Many2many('product.category', 'payment_term_product_category_rel', 'payment_term_id',
                                            'product_category_id', string='Excluded Product Categories')
    payment_term_discount_ids = fields.One2many('account.payment.term.discount', 'payment_term_id',
                                                string='Discount Accounts')


class AccountPaymentTermDiscount(models.Model):
    _name = 'account.payment.term.discount'

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    company_id = fields.Many2one('res.company', string='Company')
    payment_discount_account = fields.Many2one('account.account', string='Customer Disc Account')
    payment_supplier_discount_account = fields.Many2one('account.account', string='Supplier Disc Account')
    customer_default_analytic_compte = fields.Many2one('account.analytic.account',
                                                       string='Customer default analytic account')
    supplier_default_analytic_compte = fields.Many2one('account.analytic.account',
                                                       string='Supplier default analytic account')

    _sql_constraints = [
        ('number_uniq', 'unique(payment_term_id, company_id)', "You can't create many lines for the same company !"),
    ]
