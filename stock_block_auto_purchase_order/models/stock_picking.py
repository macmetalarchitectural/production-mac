from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"

    date_deadline = fields.Datetime(inverse = '_set_date_deadline')

    def _compute_has_deadline_issue(self):
        for picking in self:
            if picking.date_deadline and picking.scheduled_date:
                picking.has_deadline_issue = picking.date_deadline and picking.date_deadline < picking.scheduled_date or False
            else:
                picking.has_deadline_issue = False

    def _set_date_deadline(self):
        pass
        # for move_line in self.move_lines:
        #     move_line.date_deadline = self.date_deadline

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def create(self, vals):
        vals['date_deadline'] = False
        res = super(StockMove, self).create(vals)
        return res