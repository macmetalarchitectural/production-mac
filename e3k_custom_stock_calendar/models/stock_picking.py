# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'partner_id'


    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)
    # delivery_route = fields.Selection(related='sale_id.delivery_route', string='Delivery Route', store=True)
    delivery_route_id = fields.Many2one(related='sale_id.delivery_route_id', string='Delivery Route')
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)
    flexible_date = fields.Boolean(string='Flexible Date', default=False)
    e3k_all_day = fields.Boolean(string='All Day', default=True)
    e3k_custom_display_name = fields.Char(compute='_compute_e3k_custom_display_name', string='Display Name')
    e3k_calendar_color = fields.Char(string='Calendar Color', compute='_compute_e3k_calendar_color')
    e3k_calendar_text_color = fields.Char(string='Calendar Color', compute='_compute_e3k_calendar_color')

    e3k_start_date = fields.Datetime(
        'Start Date',
        compute='_compute_e3k_start_date', inverse='_inverse_dates', store=True)
    e3k_stop_date = fields.Datetime(
        'End Date',
        compute='_compute_e3k_stop_date', inverse='_inverse_dates', store=True)

    duration = fields.Float(
        'Duration',
        compute='_compute_duration', store=True, readonly=True)

    # e3k_calendar_date_deadline = fields.Date(compute='_compute_e3k_calendar_date_deadline', default=False,)

    # @api.model
    # def _action_get_value_from_x_delivery_pickup(self):
        # fonction a executer une seule fois pour mettre a jour les valeurs
        # for rec in self.search([]):
        #     if hasattr(rec, 'x_delivery_pickup'):
        #         rec.delivery_pickup = rec.x_delivery_pickup
        # self.search([])._compute_e3k_calendar_color()._compute_e3k_custom_display_name()


    @api.depends('partner_id', 'partner_id.city', 'worksite_ready', 'origin')
    def _compute_e3k_custom_display_name(self):
        for rec in self:
            sale_name = False
            city = False
            mark_for_non_ready_work = "-"
            if rec.origin:
                sale_name = rec.origin
            if rec.partner_id.city:
                city = rec.partner_id.city

            rec.e3k_custom_display_name = f"{mark_for_non_ready_work if rec.worksite_ready else ''} {rec.partner_id.name} / {sale_name if sale_name else ''} / { city if city else ''}"

    def _get_e3k_calendar_color(self):
        self.ensure_one()

        product_code_to_check = ['SER0028']
        white = '#FFFFFF'
        black = '#000000'

        color_code = {
            'Route1': {
                'color': '#ffccff',  # Pink (ROSE)
                'text_color': black,  # Black (NOIR)
            },
            'Route2': {
                'color': '#91c7ed',  # Light Blue (BLEU)
                'text_color': black,  # Black (NOIR)
            },
            'Route3': {
                'color': '#f2af9b',  # Orange (ORANGE)
                'text_color': black,  # Black (NOIR)
            },
            'Route4': {
                'color': '#996632',  # Brown (BRUN)
                'text_color': white,  # White (BLANC)
            },
            'Route5_yes_dp': {
                'color': '#919191',  # Black (NOIR)
                'text_color': white,  # White (BLANC)
            },
            'Route5_no_dp': {
                'color': '#9fcc97',  # Green (VERT)
                'text_color': black,  # Black (NOIR)
            },
            'Route6_producct_code_found': {
                'color': '#F075B5',  # Pink (ROSE)
                'text_color': black,  # Black (NOIR)
            },
            'Route6_no_dp': {
                'color': '#FF0000',  # Red (ROUGE)
                'text_color': white,  # White (BLANC)
            },
            'Route6_yes_dp': {
                'color': '#919191',  # Black (NOIR)
                'text_color': white,  # White (BLANC)
            },
        }
        delivery_route_code = self.delivery_route_id.code
        if delivery_route_code in ('Route1', 'Route2', 'Route3', 'Route4'):
            return color_code[delivery_route_code]['color'], color_code[delivery_route_code]['text_color']
        elif delivery_route_code == 'Route5':
            if self.delivery_pickup:
                return color_code['Route5_yes_dp']['color'], color_code['Route5_yes_dp']['text_color']
            else:
                return color_code['Route5_no_dp']['color'], color_code['Route5_no_dp']['text_color']
        elif delivery_route_code == 'Route6':
            so_all_product_default_code = self.sale_id.order_line.mapped('product_id.default_code')
            if list(set(product_code_to_check) & set(so_all_product_default_code)):
                return color_code['Route6_producct_code_found']['color'], color_code['Route6_producct_code_found']['text_color']
            elif not self.delivery_pickup:
                return color_code['Route6_no_dp']['color'], color_code['Route6_no_dp']['text_color']
            else:
                return color_code['Route6_yes_dp']['color'], color_code['Route6_yes_dp']['text_color']
        else:
            return white, black

    @api.depends('delivery_route', 'delivery_pickup', 'sale_id.order_line.product_id.default_code')
    def _compute_e3k_calendar_color(self):
        # Checking conditions for delivery type
        for rec in self:
            rec.e3k_calendar_color , rec.e3k_calendar_text_color = rec._get_e3k_calendar_color()

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if not start or not stop:
            return 0
        duration = (stop - start).total_seconds() / 3600
        return round(duration, 2)

    @api.depends('e3k_start_date', 'e3k_stop_date')
    def _compute_duration(self):
        for pick in self:
            pick.duration = self._get_duration(pick.e3k_start_date, pick.e3k_stop_date)

    @api.depends('e3k_all_day', 'date_deadline')
    def _compute_e3k_stop_date(self):
        for pick in self:
            if pick.e3k_all_day and pick.date_deadline:
                deadline = fields.Datetime.from_string(pick.date_deadline)
                pick.e3k_stop_date = deadline.replace(hour=18)
            else:
                pick.e3k_stop_date = False

    @api.depends('e3k_stop_date')
    def _compute_e3k_start_date(self):
        for pick in self:
            if pick.e3k_stop_date:
                deadline = fields.Datetime.from_string(pick.e3k_stop_date)
                pick.e3k_start_date = deadline.replace(hour=8)
            else:
                pick.e3k_start_date = False

    def _inverse_dates(self):
        for pick in self:
            if pick.e3k_all_day:
                deadline = fields.Datetime.from_string(pick.date_deadline)
                new_deadline = deadline.replace(day=pick.e3k_stop_date.day)
                pick.write({
                    'date_deadline': new_deadline,
                })