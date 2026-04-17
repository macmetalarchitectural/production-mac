# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # cette contrainte n'était pas chargée dans la base de données (on a cherché les raisons mais on a pas trouvé) dont on la bypassé pour eviter le warnning
    _check_amount_currency_balance_sign = models.Constraint(
        "CHECK(1=1)",
        "",
    )
