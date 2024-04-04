from odoo import models, api, fields


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=True)
    name = fields.Char(required=False)


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'

    name = fields.Char('Name', translate=True, required=True)
