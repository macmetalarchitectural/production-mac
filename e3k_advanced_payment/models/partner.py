# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.depends('child_ids')
    def _get_child_keys_ids(self):
        self.ensure_one()
        for partner in self:
            if partner.id and partner.child_ids:
                child_keys_ids = []
                for contact in partner.child_ids:
                    child_keys_ids.append(contact.id)
                self.child_keys_ids = child_keys_ids

    child_keys_ids = fields.Text(string='Difference Amount', compute='_get_child_keys_ids')
