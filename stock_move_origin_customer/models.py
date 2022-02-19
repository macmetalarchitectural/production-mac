# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api


class StockMoveOriginCustomer(models.Model):

    _inherit = 'stock.move'

    origin_customer_id = fields.Many2one(
        'res.partner', copy=False, readOnly=True, compute='_compute_origin_customer_id',
        help="Partner that is on the sale order related to the stock move.")

    @api.depends('picking_id')
    def _compute_origin_customer_id(self):
        for record in self:
            sale_order = self.env['sale.order'].search([('name', '=', record.picking_id.purchase_id.origin)])
            record.origin_customer_id = sale_order.partner_id.id
