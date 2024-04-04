from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_status_id = fields.Many2one('contact.status', string='Status')
    contact_ids = fields.One2many('res.partner', 'parent_id', string='Contacts',
                                  domain=[('active', '=', True), ('type', '=', 'contact')])
    delivery_address_ids = fields.One2many('res.partner', 'parent_id', string='Delivery Addresses',
                                           domain=[('active', '=', True), ('type', '=', 'delivery')])
    invoice_address_ids = fields.One2many('res.partner', 'parent_id', string='Invoice Addresses',
                                          domain=[('active', '=', True), ('type', '=', 'invoice')])
    other_address_ids = fields.One2many('res.partner', 'parent_id', string='Other Addresses',
                                        domain=[('active', '=', True), ('type', '=', 'other')])
    private_address_ids = fields.One2many('res.partner', 'parent_id', string='Private Addresses',
                                          domain=[('active', '=', True), ('type', '=', 'private')])

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

