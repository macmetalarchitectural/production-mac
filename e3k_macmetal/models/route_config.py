# -*- coding: utf-8 -*-

from odoo import fields, models

class MacRouteConfig(models.Model):
    _name = 'mac.route.config'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')