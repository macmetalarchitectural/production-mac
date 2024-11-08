# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'partner_id'


    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)
    delivery_route = fields.Selection(related='sale_id.delivery_route', string='Delivery Route', store=True)
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)
    flexible_date = fields.Boolean(string='Flexible Date', default=False)
    e3k_all_day = fields.Boolean(string='All Day', default=True)
    e3k_custom_display_name = fields.Char(compute='_compute_e3k_custom_display_name', string='Display Name')
    e3k_calendar_color = fields.Char(string='Calendar Color', compute='_compute_e3k_calendar_color')
    e3k_calendar_text_color = fields.Char(string='Calendar Color', compute='_compute_e3k_calendar_color')
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

        product_code_to_check = ('SER0028')
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

        if self.delivery_route in ('Route1', 'Route2', 'Route3', 'Route4'):
            return color_code[self.delivery_route]['color'], color_code[self.delivery_route]['text_color']
        elif self.delivery_route == 'Route5':
            if self.delivery_pickup:
                return color_code['Route5_yes_dp']['color'], color_code['Route5_yes_dp']['text_color']
            else:
                return color_code['Route5_no_dp']['color'], color_code['Route5_no_dp']['text_color']
        elif self.delivery_route == 'Route6':
            so_all_product_default_code = set(self.sale_id.order_line.mapped('product_id.default_code'))
            if list(product_code_to_check & so_all_product_default_code):
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