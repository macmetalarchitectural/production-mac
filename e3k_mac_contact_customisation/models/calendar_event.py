from odoo import models, api, fields, _
from datetime import datetime, timedelta, time
import pytz


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=True)
    name = fields.Char(default=lambda self: _('New'), translate=True)
    team_id = fields.Many2one('representative.team', string='Team', compute='_compute_team_rep_id', store=True)
    company_partner_id = fields.Many2one('res.partner', string='Company name', compute='_compute_company_partner_id', store=True)
    customer_state = fields.Selection(related='partner_id.customer_state', string='Status', store=True)
    rep_id = fields.Many2one('res.partner', string='Representative', related='user_id.partner_id', store=True)
    contact_ids = fields.Many2many('res.partner', string='Contacts', relation='calendar_event_contact_id', column1='calendar_event_id',
                                   column2='contact_id', compute='compute_contact_id', store=True)
    contact_name = fields.Char(related='partner_id.name', string='Contact Name', store=True)
    function = fields.Char(related='partner_id.function', string='Customer type', store=True)
    completed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Completed', default='no')

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

    @api.depends('user_id')
    def _compute_team_rep_id(self):
        for rec in self:
            if rec.user_id:
                team = self.env['representative.team'].search([('member_ids', 'in', rec.user_id.id)], limit=1)
                rec.team_id = team.id if team else False
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
        self._cr.execute(''' select id, name FROM representative_team  ORDER BY name ASC ''')
        record = self._cr.dictfetchall()
        return record

    @api.model
    def get_rep(self):
        """Get the list of representatives for the activity dashboard"""
        self._cr.execute('''
            SELECT DISTINCT t.user_id, p.id, p.name FROM calendar_event t, res_users r, res_partner p WHERE t.user_id = r.id AND r.partner_id = p.id ORDER BY p.name ASC
            ''')

        records = self._cr.dictfetchall()
        return records

    @api.model
    def get_status(self):
        """Get the list of status for the activity dashboard"""
        self._cr.execute(''' select id, name FROM contact_status  ORDER BY name ASC''')

        record = self._cr.dictfetchall()
        return record

    @api.model
    def get_meeting_type(self):
        """Get the list of meeting type for the activity dashboard"""
        self._cr.execute(''' select id, name FROM calendar_event_type  ORDER BY name ASC''')

        record = self._cr.dictfetchall()
        return record

    def adjust_dates(self, args):
        args = list(args)
        if not args[0]:
            args[0] = '1800-01-01 00:00'
        if not args[1]:
            args[1] = '2070-01-01 23:59'
        return args

    @api.model
    def get_activity_details(self):
        """Get the details of the activity for the activity dashboard"""
        self._cr.execute('''
            SELECT
                COUNT(c.id) AS activity_quantity,
                c.team_id AS team_id,
                m.name AS team_name,
                c.rep_id AS rep_id,
                a.name AS rep,
                c.meeting_type_id AS meeting_type_id,
                t.name AS meeting_type,
                p.parent_id AS parent_id,
                p.contact_status_id AS contact_status_id,
                s.name AS status,
                r.industry_id AS industry_id,
                i.name AS customer_type,
                r.name AS company_name,
                e.contact_id AS contact_id,
                p.name AS contact,
                c.completed AS completed
            FROM
                calendar_event c
            LEFT JOIN
                calendar_event_contact_id e ON e.calendar_event_id = c.id
            LEFT JOIN
                res_partner p ON p.id = e.contact_id
            LEFT JOIN
                calendar_event_type t ON t.id = c.meeting_type_id
            LEFT JOIN
                res_partner r ON r.id = p.parent_id
            LEFT JOIN
                res_partner_industry i ON i.id = r.industry_id
            LEFT JOIN
                contact_status s ON s.id = p.contact_status_id
            LEFT JOIN
                representative_team m ON m.id = c.team_id
            LEFT JOIN
                res_partner a ON a.id = c.rep_id
            GROUP BY
                c.team_id,
                m.name,
                c.rep_id,
                a.name,
                c.meeting_type_id,
                t.name,
                p.parent_id,
                p.contact_status_id,
                s.name,
                r.industry_id,
                i.name,
                r.name,
                e.contact_id,
                p.name,
                c.completed
            ORDER BY
                 COUNT(c.id) DESC
                
        ''')
        record = self._cr.dictfetchall()
        return record

    @api.model
    def get_activity_details_by_filter(self, *args):
        team_ids = args[0]
        rep_ids = args[1]
        meeting_type_ids = args[2]
        open_closed = args[3]
        status = args[4]
        dates = args[5]
        date_from = dates[0].replace('T', ' ') if dates[0] else '1800-01-01 00:00'
        date_to = dates[1].replace('T', ' ') if dates[1] else '2070-01-01 23:59'
        query = '''
            SELECT
                COUNT(c.id) AS activity_quantity,
                c.team_id AS team_id,
                m.name AS team_name,
                c.rep_id AS rep_id,
                a.name AS rep,
                c.meeting_type_id AS meeting_type_id,
                t.name AS meeting_type,
                p.parent_id AS parent_id,
                p.contact_status_id AS contact_status_id,
                s.name AS status,
                r.industry_id AS industry_id,
                i.name AS customer_type,
                r.name AS company_name,
                e.contact_id AS contact_id,
                p.name AS contact,
                c.completed AS completed
            FROM
                calendar_event c
            LEFT JOIN
                calendar_event_contact_id e ON e.calendar_event_id = c.id
            LEFT JOIN
                res_partner p ON p.id = e.contact_id
            LEFT JOIN
                calendar_event_type t ON t.id = c.meeting_type_id
            LEFT JOIN
                res_partner r ON r.id = p.parent_id
            LEFT JOIN
                res_partner_industry i ON i.id = r.industry_id
            LEFT JOIN
                contact_status s ON s.id = p.contact_status_id
            LEFT JOIN
                representative_team m ON m.id = c.team_id
            LEFT JOIN
                res_partner a ON a.id = c.rep_id
        '''

        params = ()

        if team_ids:
            query += ' WHERE c.team_id IN %s '
            params = (tuple(team_ids),)
        if rep_ids:
            if team_ids:
                query += ' AND c.rep_id IN %s '
            else:
                query += ' WHERE c.rep_id IN %s '
            params += (tuple(rep_ids),)
        if meeting_type_ids:
            if team_ids or rep_ids:
                query += ' AND c.meeting_type_id IN %s '
            else:
                query += ' WHERE c.meeting_type_id IN %s '
            params += (tuple(meeting_type_ids),)
        if open_closed:
            if team_ids or rep_ids or meeting_type_ids:
                query += ' AND c.completed IN %s '
            else:
                query += ' WHERE c.completed IN %s '
            params += (tuple(open_closed),)
        if status:
            if team_ids or rep_ids or meeting_type_ids or open_closed:
                query += ' AND p.contact_status_id IN %s '
            else:
                query += ' WHERE p.contact_status_id IN %s '
            params += (tuple(status),)
        if dates:
            if team_ids or rep_ids or meeting_type_ids or open_closed or status:
                query += ' AND c.start >= %s AND c.stop <= %s '
            else:
                query += ' WHERE c.start >= %s AND c.stop <= %s '
            params += (date_from, date_to)

        query += '''
            GROUP BY
                c.team_id,
                m.name,
                c.rep_id,
                a.name,
                c.meeting_type_id,
                t.name,
                p.parent_id,
                p.contact_status_id,
                s.name,
                r.industry_id,
                i.name,
                r.name,
                e.contact_id,
                p.name,
                c.completed
            ORDER BY
                COUNT(c.id) DESC
        '''
        self._cr.execute(query, params)
        record = self._cr.dictfetchall()
        return record


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'

    name = fields.Char('Name', translate=True, required=True)
