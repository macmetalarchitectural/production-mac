from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _reservation_is_updatable(self, quantity, reserved_quant):
        result = super(StockMoveLine, self)._reservation_is_updatable(quantity, reserved_quant)

        if self.product_id.block_auto_purchase_order:
            return False

        return result