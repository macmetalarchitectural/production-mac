
from odoo import fields, models

class StockMove(models.Model):
  _inherit = 'stock.move'

  picking_partner_id = fields.Many2one('res.partner', 'Partner', related='picking_id.partner_id')