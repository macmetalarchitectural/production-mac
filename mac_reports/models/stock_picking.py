# -*- coding: utf-8 -*-

from odoo import _, fields, models


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'info.block.report.mixin']
    _name = 'stock.picking'

    note = fields.Html('Notes', default='<p style="font-size: 18px; font-weight: bold;"><br></p>')

    def information_block_to_display(self):
        shipping_date = self.date_done if self.state == 'done' else self.scheduled_date
        weight = (
            f"{self.shipping_weight} {self.weight_uom_name}".strip()
            if self.shipping_weight
            else False
        )
        return {
            'origin': {
                'label': _('Order') if not (self.picking_type_id.code=='outgoing' and self.origin) else _('Delivery slip'),
                'value': self.origin if not (self.picking_type_id.code=='outgoing' and self.origin) else self.name or False,
                'type': 'string',
            },
            'scheduled_date': {
                'label': _('Shipping Date'),
                'value': shipping_date or False,
                'type': 'date',
                'date_info': {'format': '%m/%d/%Y'},
            },
            'payment_term_id': {
                'label': _('Terms'),
                'value': self.sale_id.payment_term_id.name or False,
                'type': 'string',
            },
            'carrier_id': {
                'label': _('Carrier'),
                'value': self.carrier_id.name or False,
                'type': 'string',
            },
            'shipping_weight': {
                'label': _('Total Weight'),
                'value': weight,
                'type': 'string',
            },
            'carrier_tracking_ref': {
                'label': _('Tracking Number'),
                'value': self.carrier_tracking_ref or False,
                'type': 'string',
            },
            'client_order_ref': {
                'label': _('Customer Reference'),
                'value': self.sudo().sale_id.client_order_ref or False,
                'type': 'string',
            },
        }
