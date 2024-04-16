from odoo import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=True)
    name = fields.Char(default=lambda self: _('New'), translate=True)
    team_id = fields.Many2one('representative.team', string='Team', compute='_compute_team_rep_id')
    team_name = fields.Char(string='Team Name', store=True)
    company_partner_id = fields.Many2one('res.partner', string='Company name', compute='_compute_company_partner_id', store=True)
    customer_state = fields.Selection(related='partner_id.customer_state', string='Status', store=True)
    rep = fields.Char(string='Representative', related='user_id.partner_id.name', store=True)
    contact_ids = fields.Many2many('res.partner', string='Contacts', relation='calendar_event_contact_id', column1='calendar_event_id',
                                   column2='contact_id', compute='compute_contact_id', store=True)
    contact_name = fields.Char(related='partner_id.name', string='Contact Name', store=True)
    function = fields.Char(related='partner_id.function', string='Customer type', store=True)

    @api.depends('partner_ids')
    def compute_contact_id(self):
        for rec in self:
            rec.contact_ids = rec.partner_ids - rec.partner_id

    @api.depends('partner_id')
    def _compute_company_partner_id(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.parent_id:
                rec.company_partner_id = rec.partner_id.parent_id.id
            else:
                rec.company_partner_id = rec.partner_id.id

    def _compute_team_rep_id(self):
        for rec in self:
            if rec.user_id:
                team = self.env['representative.team'].search([('member_ids', 'in', rec.user_id.id)], limit=1)
                rec.team_id = team.id if team else False
                rec.team_name = team.name if team else ''
            else:
                rec.team_id = False

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('calendar.event') or _('New')
        vals['name'] = seq
        res = super(CalendarEvent, self).create(vals)
        if res.user_id.partner_id not in res.partner_ids:
            res.partner_ids = [(4, res.user_id.partner_id.id)]
        return res

    @api.depends('description')
    def _compute_display_description(self):
        for event in self:
            event.display_description = False

    def name_get(self):
        """Hide private events' name for events which don't belong to the current user
        """
        result = []
        for event in self:
            name = event.meeting_type_id.name if event.meeting_type_id else _("Unknown Meeting Type")
            if event.privacy == 'private' and event.user_id.id != self.env.uid and self.env.user.partner_id not in event.partner_ids:
                result.append((event.id, _('Busy')))
            else:
                result.append((event.id, name))
        return result

    @api.model
    def get_activity_details(self):
        """Get the details of the activity for the activity dashboard
        """
        activities = self.env['calendar.event'].search(
            [('start', '>=', fields.Datetime.now()), ('user_id', '=', self.env.uid)], limit=5)
        return activities

    @api.model
    def get_teams(self):
        """Get the list of teams for the activity dashboard"""
        self._cr.execute(''' select id, name FROM representative_team ''')
        record = self._cr.dictfetchall()
        return record

    @api.model
    def get_rep(self):
        """Get the list of representatives for the activity dashboard"""
        self._cr.execute('''
            SELECT DISTINCT t.user_id, p.name FROM calendar_event t, res_users r, res_partner p WHERE t.user_id = r.id AND r.partner_id = p.id
            ''')

        records = self._cr.dictfetchall()
        return records

    @api.model
    def get_meeting_type(self):
        """Get the list of meeting type for the activity dashboard"""
        self._cr.execute(''' select id, name FROM calendar_event_type ''')

        record = self._cr.dictfetchall()
        return record

    @api.model
    def get_activity_details(self):
        """Get the details of the activity for the activity dashboard
        """
        self._cr.execute(
            '''select count(t) as activity_quantity,c.team_name as team_name, c.rep as rep ,c.meeting_type_id as meeting_type_id, t.name as meeting_type, p.parent_id as parent_id,p.contact_status_id as contact_status_id, s.name as status ,
            r.industry_id as industry_id, i.name as customer_type, r.name as company_name, e.contact_id as contact_id, p.name as contact FROM calendar_event c, res_partner p, res_partner r, calendar_event_type t, calendar_event_contact_id e, 
            res_partner_industry i, contact_status s WHERE p.id = e.contact_id AND s.id= p.contact_status_id AND e.calendar_event_id = c.id AND t.id= c.meeting_type_id AND r.id = p.parent_id  AND i.id = r.industry_id GROUP BY e.contact_id, 
            c.meeting_type_id, t.name, p.name, c.rep, c.contact_name, c.team_name, p.name, r.name, p.parent_id, r.industry_id, i.name, p.contact_status_id, s.name''')
        record = self._cr.dictfetchall()
        return record


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'

    name = fields.Char('Name', translate=True, required=True)
