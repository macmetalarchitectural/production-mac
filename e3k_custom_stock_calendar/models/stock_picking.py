# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'partner_id'


    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)
    flexible_date = fields.Boolean(string='Flexible Date', default=False)
    e3k_all_day = fields.Boolean(string='All Day', default=True)
    e3k_custom_display_name = fields.Char(compute='_compute_e3k_custom_display_name', store=True, string='Display Name')

    @api.model
    def _action_get_value_from_x_delivery_pickup(self):
        # fonction a executer une seule fois pour mettre a jour les valeurs
        for rec in self.search([]):
            if hasattr(rec, 'x_delivery_pickup'):
                rec.delivery_pickup = rec.x_delivery_pickup

    @api.depends('partner_id', 'date_deadline', 'partner_id.city')
    def _compute_e3k_custom_display_name(self):
        for rec in self:
            sep = ' - '
            date = False
            city = False
            if rec.date_deadline:
                date = sep + rec.date_deadline.strftime('%d/%m/%Y')
            if rec.partner_id.city:
                city = sep + rec.partner_id.city
            rec.e3k_custom_display_name = f"{rec.partner_id.name}  {date if date else ''}  { city if city else ''}"

