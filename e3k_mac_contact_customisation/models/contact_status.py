# -*- coding: utf-8 -*-

from random import randint

from odoo import fields, models


class ContactStatus(models.Model):
    _name = "contact.status"
    _description = 'contact Status'

    name = fields.Char('Status Name', required=True, translate=True)
