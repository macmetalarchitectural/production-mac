# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_pickup = fields.Boolean(string='Delivery Pickup', default=False)  # no-check
    e3k_delivery_on_hold = fields.Boolean(  # no-check
        string="Delivery On Hold",
        default=False,
    )
    e3k_currency_id = fields.Many2one(  # no-check
        related="company_id.currency_id",
    )
    e3k_sales_value = fields.Monetary(  # no-check
        string="Sales Value",
        currency_field="e3k_currency_id",
        readonly=True,
        compute="_compute_e3k_sales_value",
    )

    @api.depends('reference_ids.sale_ids', 'move_ids.sale_line_id.order_id')
    def _compute_sale_id(self):
        super()._compute_sale_id()

        for picking in self.filtered(lambda p:
                                     not p.sale_id and
                                     p.picking_type_id.code in ('internal', 'outgoing')):
            # picking and move should have a link to the SO to see the picking on the stat button.
            # This will filter the move chain to the delivery moves only.
            sales_order = picking.reference_ids.mapped('sale_ids') or picking.move_ids.mapped('sale_line_id.order_id')
            picking.sale_id = sales_order and sales_order[0] or False

    def _create_backorder(self):
        backorders = super()._create_backorder()
        backorders._compute_sale_id()
        return backorders

    def _compute_e3k_sales_value(self):
        for record in self:
            total_val = 0.0
            # On ne calcule que pour les sorties
            if record.picking_type_code == 'outgoing':

                # MODIFICATION 1: Boucler sur 'move_ids' (les Mouvements)
                for move in record.move_ids:

                    # On trouve la ligne de commande client liée (directement sur le move)
                    sale_line = move.sale_line_id

                    if sale_line:
                        # Calcule le prix après remise
                        price_after_discount = sale_line.price_unit * (1 - (sale_line.discount or 0.0) / 100.0)

                        # MODIFICATION 2: Utiliser 'product_uom_qty' (Quantité Demandée)
                        total_val += (move.product_uom_qty * price_after_discount)

            record.e3k_sales_value = total_val
