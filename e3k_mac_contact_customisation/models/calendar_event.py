import calendar
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.tools import format_date

# ── SQL partagé entre get_activity_details et get_activity_details_by_filter ──

_ACTIVITY_SELECT = """
    SELECT
        COUNT(c.id)             AS activity_quantity,
        c.team_id               AS team_id,
        m.name                  AS team_name,
        c.rep_id                AS rep_id,
        a.name                  AS rep,
        c.meeting_type_id       AS meeting_type_id,
        t.name                  AS meeting_type,
        p.contact_status_id     AS contact_status_id,
        s.name                  AS status,
        r.industry_id           AS industry_id,
        i.name                  AS customer_type,
        r.name                  AS company_name,
        p.name                  AS contact,
        c.completed             AS completed
    FROM calendar_event c
    LEFT JOIN res_partner         p ON p.id = c.contact_id
    LEFT JOIN calendar_event_type t ON t.id = c.meeting_type_id
    LEFT JOIN res_partner         r ON r.id = c.company_partner_id
    LEFT JOIN res_partner_industry i ON i.id = p.industry_id
    LEFT JOIN contact_status      s ON s.id = p.contact_status_id
    LEFT JOIN representative_team m ON m.id = c.team_id
    LEFT JOIN res_partner         a ON a.id = c.rep_id
    WHERE c.team_id IS NOT NULL
"""

_ACTIVITY_GROUP_ORDER = """
    GROUP BY
        c.team_id, m.name, c.rep_id, a.name,
        c.meeting_type_id, t.name,
        p.contact_status_id, s.name,
        r.industry_id, i.name,
        r.name, p.name, c.completed
    ORDER BY
        m.name ASC, a.name ASC,
        r.name ASC, p.name ASC,
        i.name ASC, s.name ASC, t.name ASC,
        COUNT(c.id) DESC
"""


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _default_start_date(self):
        now = datetime.now()
        next_hour = now.replace(second=0, microsecond=0, minute=0) + timedelta(hours=1)
        if next_hour.hour == 0:
            next_hour += timedelta(days=1)
        return next_hour

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=False)  # no-check
    name = fields.Char(default=lambda self: _('New'), translate=True)
    team_id = fields.Many2one(  # no-check
        'representative.team', string='Team', compute='_compute_team_rep_id', store=True
    )
    company_partner_id = fields.Many2one(  # no-check
        'res.partner', string='Company name', compute='_compute_company_partner_id', store=True
    )
    customer_state = fields.Selection(  # no-check
        related='partner_id.customer_state', string='Customer status', store=True
    )
    rep_id = fields.Many2one(  # no-check
        'res.partner', string='Representative', related='user_id.partner_id', store=True
    )
    contact_ids = fields.Many2many(  # no-check
        'res.partner',
        string='Contacts',
        relation='calendar_event_contact_id',
        column1='calendar_event_id',
        column2='contact_id',
        compute='_compute_contact_id',
        store=True,
    )
    contact_name = fields.Char(related='partner_id.name', string='Contact Name', store=True)  # no-check
    completed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Done', default='no')  # no-check
    partner_id = fields.Many2one(  # no-check
        'res.partner', string='Scheduled by', related='user_id.partner_id', readonly=True, store=True
    )
    start = fields.Datetime(  # no-check
        'Start',
        required=True,
        tracking=True,
        help="Start date of an event, without time for full days events",
        default=lambda self: self._default_start_date(),
    )
    stop = fields.Datetime(  # no-check
        'Stop',
        required=True,
        tracking=True,
        default=False,
        compute='_compute_stop',
        readonly=False,
        store=True,
        help="Stop date of an event, without time for full days events",
    )
    contact_id = fields.Many2one(  # no-check
        'res.partner', string='Contact', store=True, compute='_compute_company_partner_id'
    )
    contact_status_id = fields.Many2one(  # no-check
        'contact.status', string='Status', related='contact_id.contact_status_id', store=True
    )
    industry_id = fields.Many2one(related='contact_id.industry_id', store=True, string='Customer type')  # no-check
    duration = fields.Float('Duration', default=1)  # no-check

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
            },
        }

    def action_done(self):
        self.ensure_one()
        self.completed = 'yes'
        return {
            'id': self.id,
            'completed': self.completed,
        }

    @api.depends('partner_ids')
    def _compute_contact_id(self):
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('calendar.event') or _('New')
        ctx = {'skip_attendee_notification': True, 'no_mail_to_attendees': True}
        res = super(CalendarEvent, self.with_context(**ctx)).create(vals_list)
        for rec in res:
            if rec.user_id.partner_id not in rec.partner_ids:
                rec.with_context(**ctx).partner_ids = [(4, rec.user_id.partner_id.id)]
        return res

    def write(self, vals):
        return super(CalendarEvent, self.with_context(
            skip_attendee_notification=True,
            no_mail_to_attendees=True,
        )).write(vals)

    @api.depends('description')
    def _compute_display_description(self):
        for event in self:
            event.display_description = False

    def _compute_display_name(self):
        """Hide private events' name for events which don't belong to the current user"""
        for event in self:
            contact_name = (
                event.contact_id.display_name
                if event.contact_id
                else event.company_partner_id.display_name
                if event.company_partner_id
                else ''
            )
            meeting_type_name = event.meeting_type_id.name if event.meeting_type_id else ''
            name = f"{contact_name} - {meeting_type_name}"
            if (
                event.privacy == 'private'
                and event.user_id.id != self.env.uid
                and self.env.user.partner_id not in event.partner_ids
            ):
                event.display_name = _('Busy')
            else:
                event.display_name = name

    # ── Helpers dashboard ────────────────────────────────────────────────────

    def _translate_activity_records(self, records):
        """Traduit les champs nom dans la langue de l'utilisateur."""
        lang = self.env.user.lang
        if not lang or lang == 'en_US':
            return records
        team_model = self.env['representative.team'].with_context(lang=lang)
        status_model = self.env['contact.status'].with_context(lang=lang)
        industry_model = self.env['res.partner.industry'].with_context(lang=lang)
        meeting_type_model = self.env['calendar.event.type'].with_context(lang=lang)
        for rec in records:
            if rec.get('team_id'):
                rec['team_name'] = team_model.browse(rec['team_id']).name
            if rec.get('contact_status_id'):
                rec['status'] = status_model.browse(rec['contact_status_id']).name
            if rec.get('industry_id'):
                rec['customer_type'] = industry_model.browse(rec['industry_id']).name
            if rec.get('meeting_type_id'):
                rec['meeting_type'] = meeting_type_model.browse(rec['meeting_type_id']).name
        return records

    def _get_date_range_for_period(self, period_id):
        """Retourne (date_from, date_to) pour un identifiant de période."""
        today = fields.Date.today()
        if period_id == 'this_month':
            first = today.replace(day=1)
            _, days = calendar.monthrange(first.year, first.month)
            return datetime(first.year, first.month, 1), datetime(first.year, first.month, days, 23, 59, 59)
        if period_id == 'last_month':
            last_prev = today.replace(day=1) - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            return (
                datetime(first_prev.year, first_prev.month, 1),
                datetime(last_prev.year, last_prev.month, last_prev.day, 23, 59, 59),
            )
        if period_id == 'last_2_month':
            last_prev = today.replace(day=1) - timedelta(days=1)
            last_2prev = last_prev.replace(day=1) - timedelta(days=1)
            first_2prev = last_2prev.replace(day=1)
            return (
                datetime(first_2prev.year, first_2prev.month, 1),
                datetime(last_2prev.year, last_2prev.month, last_2prev.day, 23, 59, 59),
            )
        if period_id == 'this_year':
            return datetime(today.year, 1, 1), datetime(today.year, 12, 31, 23, 59, 59)
        if period_id == 'last_year':
            return datetime(today.year - 1, 1, 1), datetime(today.year - 1, 12, 31, 23, 59, 59)
        if period_id == 'last_2_year':
            return datetime(today.year - 2, 1, 1), datetime(today.year - 2, 12, 31, 23, 59, 59)
        return None, None

    # ── Méthodes du dashboard (appelées via RPC) ─────────────────────────────

    @api.model
    def get_teams(self):
        """Liste des équipes pour le dashboard."""
        return self.env['representative.team'].search_read([], ['name'], order='name asc', limit=None)

    @api.model
    def get_rep(self):
        """Liste des représentants (partenaires membres des équipes)."""
        teams = self.env['representative.team'].search([], limit=None)
        partners = teams.mapped('member_ids').mapped('partner_id').sorted('name')
        return [{'id': p.id, 'name': p.name} for p in partners]

    @api.model
    def get_rep_by_team(self, team_ids):
        """Liste des représentants filtrée par équipes."""
        if not team_ids:
            return self.get_rep()
        teams = self.env['representative.team'].browse(team_ids)
        partners = teams.mapped('member_ids').mapped('partner_id').sorted('name')
        return [{'id': p.id, 'name': p.name} for p in partners]

    @api.model
    def get_status(self):
        """Liste des statuts contact pour le dashboard."""
        return self.env['contact.status'].search_read([], ['name'], order='name asc', limit=None)

    @api.model
    def get_meeting_type(self):
        """Liste des types de réunion actifs pour le dashboard."""
        return self.env['calendar.event.type'].search_read([('active', '=', True)], ['name'], order='name asc')

    @api.model
    def get_period(self):
        """Liste des périodes disponibles pour le filtre."""
        today = fields.Date.today()
        lang = self.env.user.lang or 'en_US'

        def _fmt_month(d):
            return format_date(self.env, d, date_format='MMMM', lang_code=lang).capitalize()

        def _fmt_year(d):
            return format_date(self.env, d, date_format='YYYY', lang_code=lang)

        # Calcul propre des mois précédents sans recourir à timedelta(days=30)
        first_curr = today.replace(day=1)
        last_prev = first_curr - timedelta(days=1)  # dernier jour du mois précédent
        last_2prev = last_prev.replace(day=1) - timedelta(days=1)  # dernier jour d'il y a 2 mois

        return [
            {'id': '', 'name': ''},
            {'id': 'this_month', 'name': _fmt_month(today)},
            {'id': 'last_month', 'name': _fmt_month(last_prev)},
            {'id': 'last_2_month', 'name': _fmt_month(last_2prev)},
            {'id': 'this_year', 'name': _fmt_year(today)},
            {'id': 'last_year', 'name': _fmt_year(today.replace(year=today.year - 1))},
            {'id': 'last_2_year', 'name': _fmt_year(today.replace(year=today.year - 2))},
        ]

    @api.model
    def get_activity_details(self):
        """Résumé de toutes les activités pour le dashboard (sans filtre)."""
        self._cr.execute(_ACTIVITY_SELECT + _ACTIVITY_GROUP_ORDER)  # pylint: disable=E8103
        return self._translate_activity_records(self._cr.dictfetchall())

    @api.model
    def get_activity_details_by_filter(self, teams, reps, meeting_types, completed, status, dates, period):
        """Résumé des activités filtré selon les critères du dashboard."""
        query = _ACTIVITY_SELECT
        params = ()

        if teams:
            query += ' AND c.team_id IN %s'
            params += (tuple(teams),)
        if reps:
            query += ' AND c.rep_id IN %s'
            params += (tuple(reps),)
        if meeting_types:
            query += ' AND c.meeting_type_id IN %s'
            params += (tuple(meeting_types),)
        if completed:
            query += ' AND c.completed IN %s'
            params += (tuple(completed),)
        if status:
            query += ' AND p.contact_status_id IN %s'
            params += (tuple(status),)

        # Plage de dates : priorité à la période prédéfinie, sinon dates manuelles
        date_from, date_to = None, None
        if period:
            date_from, date_to = self._get_date_range_for_period(period)
        else:
            date_from = dates[0].replace('T', ' ') if dates[0] else None
            date_to = dates[1].replace('T', ' ') if dates[1] else None

        if date_from:
            query += ' AND c.start >= %s'
            params += (date_from,)
        if date_to:
            query += ' AND c.stop <= %s'
            params += (date_to,)

        query += _ACTIVITY_GROUP_ORDER
        self._cr.execute(query, params)
        return self._translate_activity_records(self._cr.dictfetchall())

    @api.model
    def _get_public_fields(self):
        public_fields = super()._get_public_fields()
        public_fields |= {
            'meeting_type_id',
            'industry_id',
            'customer_state',
            'contact_id',
            'company_partner_id',
            'contact_status_id',
        }
        return public_fields

    def action_open_composer(self):
        action = super().action_open_composer()
        if action.get("context"):
            action.get("context").update({'send_email_from_button': True})
        return action


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    def _send_invitation_emails(self):
        return False


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'
    _order = 'name'

    name = fields.Char('Name', translate=True, required=True)
    active = fields.Boolean(default=True)
