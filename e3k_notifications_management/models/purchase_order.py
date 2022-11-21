# -*- coding: utf-8 -*-
from odoo import models, api

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        result = super(E3KPurchaseOrder, self).button_confirm()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        po_vendor_follow = IrConfigParameter.get_param('po_vendor_follow')
        po_purrep_follow = IrConfigParameter.get_param('po_purrep_follow')
        po_creator_follow = IrConfigParameter.get_param('po_creator_follow')
        
        po_vendor_notify = str2bool(IrConfigParameter.get_param('po_vendor_notify'))
        po_purrep_notify = str2bool(IrConfigParameter.get_param('po_purrep_notify'))
        po_creator_notify = str2bool(IrConfigParameter.get_param('po_creator_notify'))
        partners_to_notify = []

        if po_creator_follow and (self.create_uid.partner_id.id not in self.message_follower_ids.mapped(
                'partner_id').mapped('id') or not self.message_follower_ids):
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.create_uid.partner_id.ids)
            if po_creator_notify:
                partners_to_notify.append(self.create_uid.partner_id.id)
        if po_purrep_follow and (self.user_id.partner_id.id not in self.message_follower_ids.mapped(
                'partner_id').mapped('id')or not self.message_follower_ids):
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.user_id.partner_id.ids)
            if po_purrep_notify:
                partners_to_notify.append(self.user_id.partner_id.id)
        if po_vendor_follow and (self.partner_id.id not in self.message_follower_ids.mapped(
                'partner_id').mapped('id')or not self.message_follower_ids):
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.partner_id.ids)
            if po_vendor_notify:
                partners_to_notify.append(self.partner_id.id)

        if self.message_follower_ids and self.partner_id:
            for follower in self.message_follower_ids:
                follower_to_remove_ids = self.env['mail.followers']
                if self.partner_id.id == follower.partner_id.id and not po_vendor_follow:
                    follower_to_remove_ids = follower
                if self.user_id.partner_id.id == follower.partner_id.id and not po_purrep_follow:
                    follower_to_remove_ids = follower
                if self.create_uid.partner_id.id == follower.partner_id.id and not po_creator_follow:
                    follower_to_remove_ids = follower
                if follower_to_remove_ids:
                    follower_to_remove_ids.sudo().unlink()

        self._e3k_notify_partners(partners_to_notify)
        return result

    @api.model
    def create(self, values):
        purchase = super(E3KPurchaseOrder, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)).create(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        req_quo_creator_follow =IrConfigParameter.get_param('req_quo_creator_follow')
        req_quo_purrep_follow = IrConfigParameter.get_param('req_quo_purrep_follow')
        req_quo_vendor_follow = IrConfigParameter.get_param('req_quo_vendor_follow')

        req_quo_creator_notify = str2bool(IrConfigParameter.get_param('req_quo_creator_notify'))
        req_quo_purrep_notify = str2bool(IrConfigParameter.get_param('req_quo_purrep_notify'))
        req_quo_vendor_notify = str2bool(IrConfigParameter.get_param('req_quo_vendor_notify'))
        partners_to_notify = []

        if req_quo_creator_follow and (purchase.create_uid.partner_id.id not in purchase.message_follower_ids.mapped(
                'partner_id').mapped('id') or not self.message_follower_ids):
            purchase.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(purchase.create_uid.partner_id.ids)
            if req_quo_creator_notify:
                partners_to_notify.append(purchase.create_uid.partner_id.id)
        if req_quo_purrep_follow and (purchase.user_id.partner_id.id not in purchase.message_follower_ids.mapped(
                'partner_id').mapped('id') or not self.message_follower_ids):
            purchase.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(purchase.user_id.partner_id.ids)
            if req_quo_purrep_notify:
                partners_to_notify.append(purchase.user_id.partner_id.id)
        if req_quo_vendor_follow and (purchase.partner_id.id not in purchase.message_follower_ids.mapped('partner_id').mapped(
                'id')or not self.message_follower_ids):
            purchase.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(purchase.partner_id.ids)
            if req_quo_vendor_notify:
                partners_to_notify.append(purchase.partner_id.id)

        if purchase.message_follower_ids and purchase.partner_id:
            for follower in purchase.message_follower_ids:
                follower_to_remove_ids = self.env['mail.followers']
                if purchase.partner_id.id == follower.partner_id.id and not req_quo_vendor_follow:
                    follower_to_remove_ids = follower
                if purchase.user_id.partner_id.id == follower.partner_id.id and not req_quo_purrep_follow:
                    follower_to_remove_ids = follower
                if purchase.create_uid.partner_id.id == follower.partner_id.id and not req_quo_creator_follow:
                    follower_to_remove_ids = follower
                if follower_to_remove_ids:
                    follower_to_remove_ids.sudo().unlink()

        self._e3k_notify_partners(partners_to_notify)
        return purchase
