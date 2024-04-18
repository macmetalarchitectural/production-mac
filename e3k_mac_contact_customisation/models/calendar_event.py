from odoo import models, api, fields, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    meeting_type_id = fields.Many2one('calendar.event.type', string='Meeting Type', required=True)
    name = fields.Char(default=lambda self: _('New'), translate=True)
    team_id = fields.Many2one('representative.team', string='Team', compute='_compute_team_rep_id')
    company_partner_id = fields.Many2one('res.partner', string='Company name', compute='_compute_company_partner_id',
                                         store=True)
    customer_state = fields.Selection(related='partner_id.customer_state', string='Status', store=True)
    function = fields.Char(related='partner_id.function', string='Customer type', store=True)
    completed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Completed', default='no')

    def action_done_schedule_next(self):
        print("action_done_schedule_next_test+++++++++++++++++++++++++++++++++++++++")
        self.ensure_one()
        self.action_done()
        return{
            'name': _('Schedule Next Test'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'default_partner_ids': [(4, self.partner_id.id)],
                'default_user_id': self.user_id.id,
                'default_meeting_type_id': self.meeting_type_id.id,
                'default_start': False,
                'default_stop': False,
                'default_name': self.name,
                'default_description': self.description,
                'default_location': self.location,
                'default_team_id': self.team_id.id,
                'default_completed': 'yes',
            }
        }

    def action_done(self):
        self.ensure_one()
        print(self)
        self.completed = 'yes'
        print(self.completed)
        return True



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



class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'

    name = fields.Char('Name', translate=True, required=True)
