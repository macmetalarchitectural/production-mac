from odoo import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=True)
    name = fields.Char(default=lambda self: _('New'), translate=True)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('calendar.event') or _('New')
        vals['name'] = seq
        res = super(CalendarEvent, self).create(vals)
        return res


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'

    name = fields.Char('Name', translate=True, required=True)
