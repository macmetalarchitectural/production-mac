from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, merge=True, merge_into=False):
        return super(StockMove, self)._action_confirm(merge=False, merge_into=merge_into)
