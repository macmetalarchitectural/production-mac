from odoo import fields, models, api

class Picking(models.Model):
    _inherit = "stock.picking"

    scheduled_date = fields.Datetime(default=False)

    def _compute_has_deadline_issue(self):
        for picking in self:
            if picking.date_deadline and picking.scheduled_date:
                picking.has_deadline_issue = picking.date_deadline and picking.date_deadline < picking.scheduled_date or False
            else:
                picking.has_deadline_issue = False

    def _compute_scheduled_date(self):
        pass
