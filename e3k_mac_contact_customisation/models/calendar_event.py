from odoo import models, api, fields, _
from datetime import datetime, timedelta, time
import calendar
from odoo.tools import format_date

MONTH_NAME_MAPPING = {
    'janvier': 'January',
    'février': 'February',
    'mars': 'March',
    'avril': 'April',
    'mai': 'May',
    'juin': 'June',
    'juillet': 'July',
    'août': 'August',
    'septembre': 'September',
    'octobre': 'October',
    'novembre': 'November',
    'décembre': 'December'
}


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _default_start_date(self):
        print("inside defualt start")
        now = datetime.now()
        next_hour = now.replace(second=0, microsecond=0, minute=0, hour=now.hour + 1)
        if next_hour.hour == 0:
            next_hour += timedelta(days=1)

        return next_hour

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=True)
    name = fields.Char(default=lambda self: _('New'), translate=True)
    team_id = fields.Many2one('representative.team', string='Team', compute='_compute_team_rep_id', store=True)
    company_partner_id = fields.Many2one('res.partner', string='Company name', compute='_compute_company_partner_id',
                                         store=True)
    customer_state = fields.Selection(related='partner_id.customer_state', string='Status', store=True)
    rep_id = fields.Many2one('res.partner', string='Representative', related='user_id.partner_id', store=True)
    contact_ids = fields.Many2many('res.partner', string='Contacts', relation='calendar_event_contact_id',
                                   column1='calendar_event_id',
                                   column2='contact_id', compute='compute_contact_id', store=True)
    contact_name = fields.Char(related='partner_id.name', string='Contact Name', store=True)
    function = fields.Char(related='partner_id.function', string='Customer type', store=True)
    completed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Done', default='no')
    start = fields.Datetime(
        'Start', required=True, tracking=True,
        help="Start date of an event, without time for full days events", default=_default_start_date)
    stop = fields.Datetime(
        'Stop', required=True, tracking=True, default=False,
        compute='_compute_stop', readonly=False, store=True,
        help="Stop date of an event, without time for full days events")

    contact_id = fields.Many2one('res.partner', string='Contact', store=True, compute='_compute_company_partner_id')
    duration = fields.Float('Duration', default=1)

    @api.onchange('duration')
    def _onchange_duration(self):
        if self.start:
            self.stop = self.start + timedelta(hours=self.duration)

    def action_done_schedule_next(self):
        self.ensure_one()
        self.action_done()
        default_partner_ids = [(4, partner.id) for partner in self.partner_ids]

        return {
            'name': _('Schedule Next Test'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': {
                'default_partner_ids': default_partner_ids,
                'default_user_id': self.user_id.id,
                'default_meeting_type_id': False,
                'default_start': self._default_start_date(),
                'default_stop': False,
                'default_name': False,
                'default_description': False,
                'default_location': False,
                'default_completed': 'no',
            }
        }

    def action_done(self):
        self.ensure_one()
        self.completed = 'yes'
        return True

    @api.depends('partner_ids')
    def compute_contact_id(self):
        for rec in self:
            rec.contact_ids = rec.partner_ids - rec.partner_id

    @api.depends('partner_id', 'partner_ids')
    def _compute_company_partner_id(self):
        for rec in self:
            if rec.partner_ids:
                partners = rec.partner_ids.filtered(lambda x: x != rec.partner_id)
                if partners:
                    rec.contact_id = partners[0].id
                    rec.company_partner_id = partners[0].parent_id.id if partners[0].parent_id else partners[0].id
                else:
                    rec.contact_id = False
                    rec.company_partner_id = False
            else:
                rec.contact_id = False
                rec.company_partner_id = False

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
        lang = self.env.user.lang or 'en_US'
        if lang != 'en_US':
            for rec in record:
                rec['name'] = self.env['representative.team'].with_context(lang=lang).browse(rec['id']).name
        return record

    @api.model
    def get_rep(self):
        """Get the list of representatives for the activity dashboard"""
        self._cr.execute('''
            SELECT DISTINCT t.res_users_id, p.id, p.name FROM representative_team_res_users_rel t, res_users r, res_partner p WHERE t.res_users_id = r.id AND r.partner_id = p.id ORDER BY p.name ASC
            ''')

        records = self._cr.dictfetchall()
        return records

    @api.model
    def get_rep_by_team(self, *args):
        team_ids = args[0]
        if not team_ids:
            team_ids = self.env['representative.team'].search([]).ids
        self._cr.execute('''
            SELECT DISTINCT t.res_users_id, p.id, p.name FROM representative_team_res_users_rel t, res_users r, res_partner p WHERE t.res_users_id = r.id AND r.partner_id = p.id AND t.representative_team_id IN %s ORDER BY p.name ASC
            ''', (tuple(team_ids),))

        records = self._cr.dictfetchall()
        return records

    @api.model
    def get_status(self):
        """Get the list of status for the activity dashboard"""
        lang = self.env.user.lang or 'en_US'
        self._cr.execute(''' 
                SELECT id, name 
                FROM contact_status 
                ORDER BY name ASC
            ''')
        records = self._cr.dictfetchall()
        if lang != 'en_US':
            for record in records:
                record['name'] = self.env['contact.status'].with_context(lang=lang).browse(record['id']).name

        return records

    @api.model
    def get_meeting_type(self):
        """Get the list of meeting type for the activity dashboard"""
        self._cr.execute(''' select id, name FROM calendar_event_type  ORDER BY name ASC''')

        record = self._cr.dictfetchall()
        lang = self.env.user.lang or 'en_US'
        if lang != 'en_US':
            for rec in record:
                rec['name'] = self.env['calendar.event.type'].with_context(lang=lang).browse(rec['id']).name
        return record

    def get_period_name(self, period):
        current_date = fields.Date.today()  # Get the current date
        if period == 'this_month':
            month_name = format_date(self.env, current_date, date_format='MMMM', lang_code=self.env.user.lang or 'en_US')
            return month_name.capitalize(), 'month'
        elif period == 'last_month':
            last_month_date = current_date - timedelta(days=30)
            last_month_name = format_date(self.env, last_month_date, date_format='MMMM', lang_code=self.env.user.lang or 'en_US')
            return last_month_name.capitalize(), 'month'
        elif period == 'last_2_month':
            last_2_month_date = current_date - timedelta(days=60)
            last_2_month_name = format_date(self.env, last_2_month_date, date_format='MMMM', lang_code=self.env.user.lang or 'en_US')
            return last_2_month_name.capitalize(), 'month'
        elif period == 'this_year':
            year_name = format_date(self.env, current_date, date_format='YYYY', lang_code=self.env.user.lang or 'en_US')
            return year_name, 'year'
        elif period == 'last_year':
            last_year_date = current_date - timedelta(days=365)
            last_year_name = format_date(self.env, last_year_date, date_format='YYYY', lang_code=self.env.user.lang or 'en_US')
            return last_year_name, 'year'
        elif period == 'last_2_year':
            last_2_year_date = current_date - timedelta(days=730)
            last_2_year_name = format_date(self.env, last_2_year_date, date_format='YYYY', lang_code=self.env.user.lang or 'en_US')
            return last_2_year_name, 'year'

    @api.model
    def get_period(self):
        periods = [{'id': '', 'name': ''},
                   {'id': 'this_month', 'name': self.get_period_name('this_month')[0]},
                   {'id': 'last_month', 'name': self.get_period_name('last_month')[0]},
                   {'id': 'last_2_month', 'name': self.get_period_name('last_2_month')[0]},
                   {'id': 'this_year', 'name': self.get_period_name('this_year')[0]},
                   {'id': 'last_year', 'name': self.get_period_name('last_year')[0]},
                   {'id': 'last_2_year', 'name': self.get_period_name('last_2_year')[0]}]
        return periods

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
                m.name ASC,
                a.name ASC,
                r.name ASC,
                p.name ASC,
                i.name ASC,
                s.name ASC, 
                t.name ASC,
                COUNT(c.id) DESC
        ''')
        records = self._cr.dictfetchall()
        lang = self.env.user.lang or 'en_US'
        if lang != 'en_US':
            for record in records:
                record['team_name'] = self.env['representative.team'].with_context(lang=lang).browse(record['team_id']).name
                record['status'] = self.env['contact.status'].with_context(lang=lang).browse(record['contact_status_id']).name
                record['customer_type'] = self.env['res.partner.industry'].with_context(lang=lang).browse(record['industry_id']).name
                record['meeting_type'] = self.env['calendar.event.type'].with_context(lang=lang).browse(record['meeting_type_id']).name

        return records

    def get_first_and_last_date_of_month(self, year, month):
        month = MONTH_NAME_MAPPING.get(month.lower(), month)
        month = datetime.strptime(month, '%B').month
        num_days_in_month = calendar.monthrange(year, month)[1]
        first_date_of_month = datetime(year, month, 1)
        last_date_of_month = datetime(year, month, num_days_in_month, 23, 59, 59)
        return first_date_of_month, last_date_of_month

    def get_first_and_last_date_of_year(self, year):
        first_date_of_year = datetime(year, 1, 1)
        last_date_of_year = datetime(year, 12, 31, 23, 59, 59)
        return first_date_of_year, last_date_of_year

    # Example usage:
    @api.model
    def get_activity_details_by_filter(self, *args):
        team_ids = args[0]
        rep_ids = args[1]
        meeting_type_ids = args[2]
        open_closed = args[3]
        if 'all' in open_closed:
            open_closed = ['yes', 'no']
        status = args[4]
        dates = args[5]
        date_from = dates[0].replace('T', ' ') if dates[0] else '1800-01-01 00:00'
        date_to = dates[1].replace('T', ' ') if dates[1] else '2070-01-01 23:59'
        period = args[6]
        if period:
            period = self.get_period_name(period)
            if period[1] == "month":
                current_year = datetime.now().year
                dates = self.get_first_and_last_date_of_month(current_year, period[0])
            elif period[1] == "year":
                dates = self.get_first_and_last_date_of_year(int(period[0]))
            date_from = dates[0]
            date_to = dates[1]
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
                m.name ASC,
                a.name ASC,
                r.name ASC,
                p.name ASC,
                i.name ASC,
                s.name ASC, 
                t.name ASC,
                COUNT(c.id) DESC
                    
        '''
        self._cr.execute(query, params)
        records = self._cr.dictfetchall()
        lang = self.env.user.lang or 'en_US'
        if lang != 'en_US':
            for record in records:
                record['team_name'] = self.env['representative.team'].with_context(lang=lang).browse(record['team_id']).name
                record['status'] = self.env['contact.status'].with_context(lang=lang).browse(record['contact_status_id']).name
                record['customer_type'] = self.env['res.partner.industry'].with_context(lang=lang).browse(record['industry_id']).name
                record['meeting_type'] = self.env['calendar.event.type'].with_context(lang=lang).browse(record['meeting_type_id']).name

        return records


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'
    _order = 'name'

    name = fields.Char('Name', translate=True, required=True)
    active = fields.Boolean(default=True)
