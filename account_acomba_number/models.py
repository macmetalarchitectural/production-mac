# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountAccount(models.Model):

    _inherit = 'account.account'

    acomba_number = fields.Char(
        'Acomba Account', copy=False,
        help="Acomba account number for mapping")
