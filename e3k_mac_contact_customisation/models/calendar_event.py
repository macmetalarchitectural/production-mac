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


class CalendarEventType(models.Model):
    _inherit = 'calendar.event.type'

    name = fields.Char('Name', translate=True, required=True)
