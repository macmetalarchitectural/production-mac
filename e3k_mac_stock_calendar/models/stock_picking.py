# -*- coding: utf-8 -*-

import logging
from datetime import datetime

import pytz
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_logger.info('StockPicking model loaded')


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'partner_id'

    delivery_route_id = fields.Many2one(related='sale_id.delivery_route_id', string='Delivery Route')  # no-check
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)  # no-check
    flexible_date = fields.Boolean(string='Flexible Date', default=False)  # no-check
    e3k_all_day = fields.Boolean(string='All Day', default=True)
    e3k_custom_display_name = fields.Char(compute='_compute_e3k_custom_display_name', string='Custom display Name')
    e3k_calendar_color = fields.Char(string='Calendar color', compute='_compute_e3k_calendar_color')
    e3k_calendar_text_color = fields.Char(string='Calendar text color', compute='_compute_e3k_calendar_color')

    @api.depends('partner_id', 'partner_id.city', 'worksite_ready', 'origin')
    def _compute_e3k_custom_display_name(self):
        for rec in self:
            sale_name = False
            city = False
            mark_for_non_ready_work = " - "
            if rec.origin:
                sale_name = rec.origin
            elif rec.name:
                sale_name = rec.name
            if rec.partner_id.city:
                city = rec.partner_id.city

            partner_name = rec.partner_id.name if rec.partner_id else ''
            sale_part = f' / {sale_name}' if sale_name else ''
            city_part = f' / {city}' if city else ''
            mark = mark_for_non_ready_work if rec.worksite_ready else ''
            rec.e3k_custom_display_name = f"{mark}{partner_name}{sale_part}{city_part}"

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
            'Route6_product_code_found': {
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
        if delivery_route_code == 'Route5':
            if self.delivery_pickup:
                return color_code['Route5_yes_dp']['color'], color_code['Route5_yes_dp']['text_color']
            return color_code['Route5_no_dp']['color'], color_code['Route5_no_dp']['text_color']
        if delivery_route_code == 'Route6':
            so_all_product_default_code = self.sale_id.order_line.mapped('product_id.default_code')
            if list(set(product_code_to_check) & set(so_all_product_default_code)):
                return (
                    color_code['Route6_product_code_found']['color'],
                    color_code['Route6_product_code_found']['text_color'],
                )
            if not self.delivery_pickup:
                return color_code['Route6_no_dp']['color'], color_code['Route6_no_dp']['text_color']
            return color_code['Route6_yes_dp']['color'], color_code['Route6_yes_dp']['text_color']
        return white, black

    @api.depends('delivery_route_id', 'delivery_pickup', 'sale_id.order_line.product_id.default_code')
    def _compute_e3k_calendar_color(self):
        # Checking conditions for delivery type
        for rec in self:
            rec.e3k_calendar_color, rec.e3k_calendar_text_color = rec._get_e3k_calendar_color()

    def write(self, vals):
        _logger.warning('Writing values: %s', vals)
        if 'date_deadline' in vals and vals['date_deadline']:
            user_tz = pytz.timezone(self.env.user.tz or 'UTC')

            # Dans Odoo 19, les champs Datetime retournent directement des objets datetime
            if self.date_deadline:
                # Convertir la date existante en UTC pour avoir la bonne heure
                existing_dt = (
                    self.date_deadline
                    if isinstance(self.date_deadline, datetime)
                    else fields.Datetime.to_datetime(self.date_deadline)
                )
            else:
                # Si pas de date existante, utiliser la date actuelle
                existing_dt = fields.Datetime.now()

            # Convertir la nouvelle date
            new_dt = vals.get('date_deadline')
            if isinstance(new_dt, str):
                new_dt = fields.Datetime.to_datetime(new_dt)

            # Si new_dt est naive, le localiser
            if new_dt.tzinfo is None:
                user_new_dt = user_tz.localize(new_dt)
            else:
                user_new_dt = new_dt.astimezone(user_tz)

            new_dt_utc = user_new_dt.astimezone(pytz.utc)

            # Appliquer l'heure UTC existante à la nouvelle date UTC
            final_dt_utc = new_dt_utc.replace(
                hour=existing_dt.hour,
                minute=existing_dt.minute,
                second=existing_dt.second,
                microsecond=existing_dt.microsecond,
            )
            # Odoo stocke les datetimes en UTC naïf (sans tzinfo)
            final_dt_utc = final_dt_utc.replace(tzinfo=None)
            _logger.warning('Final datetime UTC: %s', final_dt_utc)

            # Enregistrer la nouvelle date avec l'heure existante
            self.move_ids.write({'date_deadline': final_dt_utc})

            vals['date_deadline'] = final_dt_utc

        result = super().write(vals)
        return result
