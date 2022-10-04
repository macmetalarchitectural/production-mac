# -*- coding: utf-8 -*-
from odoo import models, api

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KAccountMove(models.Model):
    _inherit = "account.move"

    def action_invoice_open(self):
        res = super(E3KAccountMove, self).action_invoice_open()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        
        inv_customer_follow = IrConfigParameter.get_param('inv_customer_follow')
        bill_vendor_follow = IrConfigParameter.get_param('bill_vendor_follow')
        inv_seller_follow = IrConfigParameter.get_param('inv_seller_follow')
        bill_purrep_follow = IrConfigParameter.get_param('bill_purrep_follow')
        inv_creator_follow = IrConfigParameter.get_param('inv_creator_follow')
        bill_creator_follow = IrConfigParameter.get_param('bill_creator_follow')
        
        inv_customer_notify = str2bool(IrConfigParameter.get_param('inv_customer_notify'))
        bill_vendor_notify = str2bool(IrConfigParameter.get_param('bill_vendor_notify'))
        inv_seller_notify = str2bool(IrConfigParameter.get_param('inv_seller_notify'))
        bill_purrep_notify = str2bool(IrConfigParameter.get_param('bill_purrep_notify'))
        inv_creator_notify = str2bool(IrConfigParameter.get_param('inv_creator_notify'))
        bill_creator_notify = str2bool(IrConfigParameter.get_param('bill_creator_notify'))

        partners_to_notify = []

        if self.move_type == 'out_invoice':
            if inv_creator_follow and (self.create_uid.partner_id.id not in self.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.create_uid.partner_id.ids)
                if inv_creator_notify:
                    partners_to_notify.append(self.create_uid.partner_id.id)
            if inv_seller_follow and (self.user_id.partner_id.id not in self.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.user_id.partner_id.ids)
                if inv_seller_notify:
                    partners_to_notify.append(self.user_id.partner_id.id)
            if inv_customer_follow and (self.partner_id.id not in self.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.partner_id.ids)
                if inv_customer_notify:
                    partners_to_notify.append(self.partner_id.id)

            if self.message_follower_ids and self.partner_id:
                for follower in self.message_follower_ids:
                    follower_to_remove_ids = self.env['mail.followers']
                    if self.partner_id.id == follower.partner_id.id and not inv_customer_follow:
                        follower_to_remove_ids = follower
                    if self.user_id.partner_id.id == follower.partner_id.id and not inv_seller_follow:
                        follower_to_remove_ids = follower
                    if self.create_uid.partner_id.id == follower.partner_id.id and not inv_creator_follow:
                        follower_to_remove_ids = follower
                    if follower_to_remove_ids:
                        follower_to_remove_ids.sudo().unlink()

        elif self.move_type == 'in_invoice':
            if bill_creator_follow and (self.create_uid.partner_id.id not in self.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.create_uid.partner_id.ids)
                if bill_creator_notify:
                    partners_to_notify.append(self.create_uid.partner_id.id)
            if bill_purrep_follow and (self.user_id.partner_id.id not in self.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.user_id.partner_id.ids)
                if bill_purrep_notify:
                    partners_to_notify.append(self.user_id.partner_id.id)
            if bill_vendor_follow and (self.partner_id.id not in self.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not self.message_follower_ids):
                self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(self.partner_id.ids)
                if bill_vendor_notify:
                    partners_to_notify.append(self.partner_id.id)

            if self.message_follower_ids and self.partner_id:
                for follower in self.message_follower_ids:
                    follower_to_remove_ids = self.env['mail.followers']
                    if self.partner_id.id == follower.partner_id.id and not bill_vendor_follow:
                        follower_to_remove_ids = follower
                    if self.user_id.partner_id.id == follower.partner_id.id and not bill_purrep_follow:
                        follower_to_remove_ids = follower
                    if self.create_uid.partner_id.id == follower.partner_id.id and not bill_creator_follow:
                        follower_to_remove_ids = follower
                    if follower_to_remove_ids:
                        follower_to_remove_ids.sudo().unlink()

        self._e3k_notify_partners(partners_to_notify)

        return res

    @api.model
    def create(self, values):
        invoice = super(E3KAccountMove, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)).create(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        
        entry_customer_follow = IrConfigParameter.get_param('entry_customer_follow')
        inv_seller_follow = IrConfigParameter.get_param('inv_seller_follow')
        bill_purrep_follow = IrConfigParameter.get_param('bill_purrep_follow')
        entry_salerep_follow = IrConfigParameter.get_param('entry_salerep_follow')
        inv_creator_follow = IrConfigParameter.get_param('inv_creator_follow')
        bill_creator_follow = IrConfigParameter.get_param('bill_creator_follow')
        entry_creator_follow = IrConfigParameter.get_param('entry_creator_follow')

        entry_customer_notify = str2bool(IrConfigParameter.get_param('entry_customer_notify'))
        inv_seller_notify = str2bool(IrConfigParameter.get_param('inv_seller_notify'))
        bill_purrep_notify = str2bool(IrConfigParameter.get_param('bill_purrep_notify'))
        entry_salerep_notify = str2bool(IrConfigParameter.get_param('entry_salerep_notify'))
        inv_creator_notify = str2bool(IrConfigParameter.get_param('inv_creator_notify'))
        bill_creator_notify = str2bool(IrConfigParameter.get_param('bill_creator_notify'))
        entry_creator_notify = str2bool(IrConfigParameter.get_param('entry_creator_notify'))

        partners_to_notify = []

        if invoice.move_type == 'out_invoice':
            if inv_creator_follow and (invoice.create_uid.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.create_uid.partner_id.ids)
                if inv_creator_notify:
                    partners_to_notify.append(invoice.create_uid.partner_id.id)
            if inv_seller_follow and (invoice.user_id.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.user_id.partner_id.ids)
                if inv_seller_notify:
                    partners_to_notify.append(invoice.user_id.partner_id.id)

            if invoice.message_follower_ids and invoice.partner_id:
                for follower in invoice.message_follower_ids:
                    follower_to_remove_ids = self.env['mail.followers']
                    if invoice.partner_id.id == follower.partner_id.id :
                        follower_to_remove_ids = follower
                    if invoice.user_id.partner_id.id == follower.partner_id.id and not inv_seller_follow:
                        follower_to_remove_ids = follower
                    if invoice.create_uid.partner_id.id == follower.partner_id.id and not inv_creator_follow:
                        follower_to_remove_ids = follower
                    if follower_to_remove_ids:
                        follower_to_remove_ids.sudo().unlink()

        elif invoice.move_type == 'in_invoice':
            if bill_creator_follow and (invoice.create_uid.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.create_uid.partner_id.ids)
                if bill_creator_notify:
                    partners_to_notify.append(invoice.create_uid.partner_id.id)
            if bill_purrep_follow and (invoice.user_id.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.user_id.partner_id.ids)
                if bill_purrep_notify:
                    partners_to_notify.append(invoice.user_id.partner_id.id)

            if invoice.message_follower_ids and invoice.partner_id:
                for follower in invoice.message_follower_ids:
                    follower_to_remove_ids = self.env['mail.followers']
                    if invoice.partner_id.id == follower.partner_id.id :
                        follower_to_remove_ids = follower
                    if invoice.user_id.partner_id.id == follower.partner_id.id and not bill_purrep_follow:
                        follower_to_remove_ids = follower
                    if invoice.create_uid.partner_id.id == follower.partner_id.id and not bill_creator_follow:
                        follower_to_remove_ids = follower
                    if follower_to_remove_ids:
                        follower_to_remove_ids.sudo().unlink()

        elif invoice.move_type == 'entry':
            if entry_creator_follow and (invoice.create_uid.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.create_uid.partner_id.ids)
                if entry_creator_notify:
                    partners_to_notify.append(invoice.create_uid.partner_id.id)
            if entry_salerep_follow and (invoice.user_id.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.user_id.partner_id.ids)
                if entry_salerep_notify:
                    partners_to_notify.append(invoice.user_id.partner_id.id)
            if entry_customer_follow and (invoice.partner_id.id not in invoice.message_follower_ids.mapped(
                    'partner_id').mapped('id') or not invoice.message_follower_ids):
                invoice.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(invoice.partner_id.ids)
                if entry_customer_notify:
                    partners_to_notify.append(invoice.partner_id.id)

            if invoice.message_follower_ids and invoice.partner_id:
                for follower in invoice.message_follower_ids:
                    follower_to_remove_ids = self.env['mail.followers']
                    if invoice.partner_id.id == follower.partner_id.id and not entry_customer_follow :
                        follower_to_remove_ids = follower
                    if invoice.user_id.partner_id.id == follower.partner_id.id and not entry_salerep_follow:
                        follower_to_remove_ids = follower
                    if invoice.create_uid.partner_id.id == follower.partner_id.id and not entry_creator_follow:
                        follower_to_remove_ids = follower
                    if follower_to_remove_ids:
                        follower_to_remove_ids.sudo().unlink()

        invoice._e3k_notify_partners(partners_to_notify)

        return invoice
