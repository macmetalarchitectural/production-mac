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

    def schedule_meeting(self):
        self.ensure_one()
        partner_ids = [self.env.user.partner_id.id]
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_partner"m_ids': partner_ids,
            'create': False
        }
        action['domain'] = ['|', ('id', 'in', self._compute_meeting()[self.id]), ('partner_ids', 'in', self.ids)]
        return action