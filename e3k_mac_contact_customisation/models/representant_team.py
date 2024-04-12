# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import random

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.release import version


class RepresentativeTeam(models.Model):
    _name = "representative.team"
    _inherit = ['mail.thread']
    _description = "Representative Team"
    _order = "sequence ASC, create_date DESC, id DESC"
    _check_company_auto = True



    # description
    name = fields.Char('Representative Team', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the Sales Team without removing it.")
    company_id = fields.Many2one(
        'res.company', string='Company', index=True,
        default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', check_company=True)
    member_ids = fields.Many2many(
        'res.users', string='Team Members', check_company=True,
        help="Users assigned to this team.")

