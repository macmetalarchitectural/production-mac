# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'partner_id'


    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)
    delivery_route = fields.Selection(related='sale_id.delivery_route', string='Delivery Route', store=True)
    worksite_ready = fields.Boolean(string='Worksite Ready', default=False)
    flexible_date = fields.Boolean(string='Flexible Date', default=False)
    e3k_all_day = fields.Boolean(string='All Day', default=True)
    e3k_custom_display_name = fields.Char(compute='_compute_e3k_custom_display_name', store=True, string='Display Name')
    e3k_calendar_color = fields.Char(string='Calendar Color', compute='_compute_e3k_calendar_color', store=True)

    @api.model
    def _action_get_value_from_x_delivery_pickup(self):
        # fonction a executer une seule fois pour mettre a jour les valeurs
        for rec in self.search([]):
            if hasattr(rec, 'x_delivery_pickup'):
                rec.delivery_pickup = rec.x_delivery_pickup

    @api.depends('partner_id', 'date_deadline', 'partner_id.city', 'worksite_ready')
    def _compute_e3k_custom_display_name(self):
        for rec in self:
            sale_name = False
            city = False
            mark_for_non_ready_work = "-"
            if rec.sale_id:
                sale_name = rec.sale_id.name
            if rec.partner_id.city:
                city = rec.partner_id.city

            rec.e3k_custom_display_name = f"{mark_for_non_ready_work if rec.worksite_ready else ''} {rec.partner_id.name}  {sale_name if sale_name else ''}  { city if city else ''}"

    def _get_e3k_calendar_color(self):
        self.ensure_one()
        color = False
        if self.delivery_route == 'Route1':
            color = '#FFB6C1'  # Pink (ROSE)
        elif self.delivery_route == 'Route3':
            color = '#FFA500'  # Orange (ORANGE)
        elif self.delivery_route == 'Route2':
            color = '#ADD8E6'  # Light Blue (BLEU)
        elif self.delivery_route == 'Route4':
            color = '#8B4513'  # Brown (BRUN)

        # Checking conditions for pickup status
        elif self.delivery_pickup and self.delivery_route == 'Route5':
            color = '#000000'  # Black (NOIR)
        elif not self.delivery_pickup and self.delivery_route == 'Route5':
            color = '#008000'  # Green (VERT)

        # Target conditions based on product codes in SO lines
        elif self.delivery_route == 'Route6':
            so_all_product_default_code = self.sale_id.order_line.mapped('product_id.default_code')
            if 'SER0028' in so_all_product_default_code:
                color = '#FF00FF'  # Magenta (MAUVE)
            elif not self.delivery_pickup:
                color = '#FF0000'  # Red (ROUGE)
            else:
                color = '#000000'  # Black (NOIR)
        return color
    @api.depends('delivery_route', 'delivery_pickup', 'sale_id.order_line.product_id.default_code')
    def _compute_e3k_calendar_color(self):
        # Checking conditions for delivery type
        for rec in self:
            rec.e3k_calendar_color = rec._get_e3k_calendar_color()