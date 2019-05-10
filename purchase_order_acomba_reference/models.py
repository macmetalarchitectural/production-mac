# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    acomba_reference = fields.Char('Acomba Reference')
