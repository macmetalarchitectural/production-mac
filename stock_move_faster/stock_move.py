# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMoveWithFasterActionDone(models.Model):

    _inherit = 'stock.move'

    def _action_done(self):
        # This improvement causes a side effect for stock moves related to a picking.
        # The super()._action_done method does operations on the picking,
        # so it must be called once with all stock moves.
        is_related_to_picking = bool(self.mapped('picking_id'))
        if is_related_to_picking:
            return super()._action_done()

        result = self.env['stock.move']
        for move in self:
            single_move = self.browse(move.id)
            result |= super(StockMoveWithFasterActionDone, single_move)._action_done()

        return result
