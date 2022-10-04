# -*- coding: utf-8 -*-
from odoo import models, api, fields

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KResPartner(models.Model):
    _inherit = "res.partner"

    user_id = fields.Many2one(
        tracking=False
    )

    @api.model
    def create(self, values):
        contact = super(E3KResPartner, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)).create(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        cont_creator_follow = IrConfigParameter.get_param('cont_creator_follow')
        cont_salerep_follow = IrConfigParameter.get_param('cont_salerep_follow')
        cont_customer_follow = IrConfigParameter.get_param('cont_customer_follow')

        cont_salerep_notify = str2bool(IrConfigParameter.get_param('cont_salerep_notify'))
        cont_customer_notify = str2bool(IrConfigParameter.get_param('cont_customer_notify'))

        partners_to_notify = []

        if cont_salerep_follow and (contact.user_id.partner_id.id not in contact.message_follower_ids.mapped(
                'partner_id').mapped('id') or not self.message_follower_ids):
            contact.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(contact.user_id.partner_id.ids)
            if cont_salerep_notify:
                partners_to_notify.append(contact.user_id.partner_id.id)


        if cont_customer_follow:
            for child in contact.child_ids:
                if (child.id not in contact.message_follower_ids.mapped(
                        'partner_id').mapped('id') or not self.message_follower_ids):
                    contact.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(child.ids)
                    if cont_customer_notify:
                        partners_to_notify.append(child.id)

        if contact.message_follower_ids:
            for follower in contact.message_follower_ids:
                follower_to_remove_ids = self.env['mail.followers']
                if contact.user_id:
                    if contact.user_id.partner_id.id == follower.partner_id.id and not cont_salerep_follow:
                        follower_to_remove_ids = follower

                if contact.create_uid.partner_id.id == follower.partner_id.id and not cont_creator_follow:
                    follower_to_remove_ids = follower

                if follower_to_remove_ids:
                    follower_to_remove_ids.sudo().unlink()


        self._e3k_notify_partners(partners_to_notify)

        return contact

    def write(self, values):
        contact = super(E3KResPartner, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)).write(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        partners_to_notify = []

        for rec in self:
            cont_customer_follow = IrConfigParameter.sudo().get_param('cont_customer_follow')
            cont_salerep_follow = IrConfigParameter.sudo().get_param('cont_salerep_follow')

            cont_customer_notify = str2bool(IrConfigParameter.sudo().get_param('cont_customer_notify'))
            cont_salerep_notify = str2bool(IrConfigParameter.sudo().get_param('cont_salerep_notify'))
            
            if cont_salerep_follow and (rec.user_id.partner_id.id not in rec.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                rec.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(rec.user_id.partner_id.ids)
                if cont_salerep_notify:
                    partners_to_notify.append(rec.user_id.partner_id.id)

            if cont_customer_follow:
                for child in rec.child_ids:
                    if (child.id not in rec.message_follower_ids.mapped(
                            'partner_id').mapped('id') or not rec.message_follower_ids):
                        rec.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(child.ids)
                        if cont_customer_notify:
                            partners_to_notify.append(child.id)

        self._e3k_notify_partners(partners_to_notify)
        return contact
