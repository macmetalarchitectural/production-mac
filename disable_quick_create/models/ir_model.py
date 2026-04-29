# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class IrModel(models.Model):

    _inherit = 'ir.model'

    disable_create_edit = fields.Boolean('Disable the Create and Edit option')

    @api.model
    def get_disable_create_edit(self, res_model):
        result = self.sudo().search_read(
            [['model', '=', res_model]],
            ['disable_create_edit'],
            limit=1,
        )
        return result[0]['disable_create_edit'] if result else False
