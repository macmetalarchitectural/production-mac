from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_status_id = fields.Many2one('contact.status', string='Status', store=True)
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

    def open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'name': 'Record name',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.contact_status_id = self.parent_id.contact_status_id
            self.industry_id = self.parent_id.industry_id

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        # if contact_status_id is changed, update the contact_status_id of all contacts
        if 'contact_status_id' in vals:
            # search all contacts that has parent_id = self.id
            for rec in self:
                contacts = self.env['res.partner'].search([('parent_id', '=', rec.id)])
                if contacts:
                    contacts.write({'contact_status_id': vals['contact_status_id']})

        return res

    @api.onchange('industry_id')
    def _onchange_contact_status_or_industry(self):
        contacts = self.env['res.partner'].search([('parent_id', '=', self.id)])
        values_to_update = {}
        if self.industry_id:
            values_to_update['industry_id'] = self.industry_id.id
        if values_to_update:
            contacts.write(values_to_update)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        # if parent_id has industry_id and contact_status_id, update the industry_id and contact_status_id of this new contact
        if self.parent_id:
            if self.parent_id.industry_id:
                res.update({'industry_id': self.parent_id.industry_id.id})
            if self.parent_id.contact_status_id:
                res.update({'contact_status_id': self.parent_id.contact_status_id.id})
        return res


# inherit calendar.attendee
class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(self, mail_template, force_send=False):
        # get context from the
        context = self._context
        if context.get('default_res_model') == 'res.partner':
            return
        else:
            return super(CalendarAttendee, self)._send_mail_to_attendees(mail_template, force_send)
