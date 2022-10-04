# -*- coding: utf-8 -*-
from odoo import models, api

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KSaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super(E3KSaleOrder, self).action_confirm()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        so_customer_follow = IrConfigParameter.get_param('so_customer_follow')
        so_seller_follow = IrConfigParameter.get_param('so_seller_follow')
        so_creator_follow = IrConfigParameter.get_param('so_creator_follow')

        so_customer_notify = str2bool(IrConfigParameter.get_param('so_customer_notify'))
        so_seller_notify = str2bool(IrConfigParameter.get_param('so_seller_notify'))
        so_creator_notify = str2bool(IrConfigParameter.get_param('so_creator_notify'))

        partners_to_notify = []

        if so_creator_follow and (self.create_uid.partner_id.id not in self.message_follower_ids.mapped(
                'partner_id').mapped('id') or not self.message_follower_ids):
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.create_uid.partner_id.ids)
            if so_creator_notify:
                partners_to_notify.append(self.create_uid.partner_id.id)

        if so_seller_follow and (self.user_id.partner_id.id not in self.message_follower_ids.mapped(
                'partner_id').mapped('id') or not self.message_follower_ids):
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.user_id.partner_id.ids)
            if so_seller_notify:
                partners_to_notify.append(self.user_id.partner_id.id)

        if so_customer_follow and (self.partner_id.id not in self.message_follower_ids.mapped(
                'partner_id').ids or not self.message_follower_ids):
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.partner_id.ids)
            if so_customer_notify:
                partners_to_notify.append(self.partner_id.id)
            
        if self.message_follower_ids and self.partner_id:
            for follower in self.message_follower_ids:
                follower_to_remove_ids = self.env['mail.followers']
                if (self.partner_id.id == follower.partner_id.id) and not so_customer_follow:
                    follower_to_remove_ids = follower
                if (self.user_id.partner_id.id == follower.partner_id.id) and not so_seller_follow:
                    follower_to_remove_ids = follower
                if (self.create_uid.partner_id.id == follower.partner_id.id) and not so_creator_follow:
                    follower_to_remove_ids = follower
                if follower_to_remove_ids:
                    follower_to_remove_ids.sudo().unlink()

        # Notify partners
        self._e3k_notify_partners(partners_to_notify)

        return result

    @api.model
    def create(self, values):
        sale = super(E3KSaleOrder, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True
        )).create(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        quo_creator_follow = IrConfigParameter.get_param('quo_creator_follow')
        quo_salerep_follow = IrConfigParameter.get_param('quo_salerep_follow')
        quo_customer_follow = IrConfigParameter.get_param('quo_customer_follow')

        quo_creator_notify = str2bool(IrConfigParameter.get_param('quo_creator_notify'))
        quo_salerep_notify = str2bool(IrConfigParameter.get_param('quo_salerep_notify'))
        quo_customer_notify = str2bool(IrConfigParameter.get_param('quo_customer_notify'))

        partners_to_notify = []

        if quo_creator_follow and (sale.create_uid.partner_id.id not in sale.message_follower_ids.mapped('partner_id').mapped('id')or not self.message_follower_ids):
            sale.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(sale.create_uid.partner_id.ids)
            if quo_creator_notify:
                partners_to_notify.append(sale.create_uid.partner_id.id)

        if quo_salerep_follow and (sale.user_id.partner_id.id not in sale.message_follower_ids.mapped('partner_id').mapped('id')or not self.message_follower_ids):
            sale.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(sale.user_id.partner_id.ids)
            if quo_salerep_notify:
                partners_to_notify.append(sale.user_id.partner_id.id)

        if quo_customer_follow and (sale.partner_id.id not in sale.message_follower_ids.mapped('partner_id').mapped('id')or not self.message_follower_ids):
            sale.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(sale.partner_id.ids)
            if quo_customer_notify:
                partners_to_notify.append(sale.partner_id.id)

        if sale.message_follower_ids and sale.partner_id:
            follower_to_remove_ids = self.env['mail.followers']

            for follower in sale.message_follower_ids:
                if sale.partner_id.id == follower.partner_id.id and not quo_customer_follow:
                    follower_to_remove_ids = follower
                if sale.user_id.partner_id.id == follower.partner_id.id and not quo_salerep_follow:
                    follower_to_remove_ids = follower
                if sale.create_uid.partner_id.id == follower.partner_id.id and not quo_creator_follow:
                    follower_to_remove_ids = follower

            if follower_to_remove_ids:
                follower_to_remove_ids.sudo().unlink()

        # Notify partners
        sale._e3k_notify_partners(partners_to_notify)

        return sale
