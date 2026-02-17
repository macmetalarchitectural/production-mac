# -*- coding: utf-8 -*-
from odoo import api, models


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KAccountMove(models.Model):
    _inherit = "account.move"

    def _get_notification_params(self):
        """Récupère les paramètres de configuration pour les notifications et abonnements."""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        return {
            'follow': {
                'entry_customer': IrConfigParameter.get_param('entry_customer_follow'),
                'inv_seller': IrConfigParameter.get_param('inv_seller_follow'),
                'inv_customer': IrConfigParameter.get_param('inv_customer_follow'),
                'bill_purrep': IrConfigParameter.get_param('bill_purrep_follow'),
                'entry_salerep': IrConfigParameter.get_param('entry_salerep_follow'),
                'inv_creator': IrConfigParameter.get_param('inv_creator_follow'),
                'bill_creator': IrConfigParameter.get_param('bill_creator_follow'),
                'entry_creator': IrConfigParameter.get_param('entry_creator_follow'),
            },
            'notify': {
                'entry_customer': str2bool(IrConfigParameter.get_param('entry_customer_notify')),
                'inv_seller': str2bool(IrConfigParameter.get_param('inv_seller_notify')),
                'bill_purrep': str2bool(IrConfigParameter.get_param('bill_purrep_notify')),
                'entry_salerep': str2bool(IrConfigParameter.get_param('entry_salerep_notify')),
                'inv_creator': str2bool(IrConfigParameter.get_param('inv_creator_notify')),
                'bill_creator': str2bool(IrConfigParameter.get_param('bill_creator_notify')),
                'entry_creator': str2bool(IrConfigParameter.get_param('entry_creator_notify')),
            },
        }

    def _subscribe_partner_if_needed(self, partner, follow_param, notify_param, partners_to_notify):
        """Abonne un partenaire si nécessaire et l'ajoute à la liste de notification."""
        if not partner or not follow_param:
            return

        follower_partner_ids = self.message_follower_ids.mapped('partner_id').ids
        if partner.id not in follower_partner_ids or not self.message_follower_ids:
            self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe([partner.id])
            if notify_param:
                partners_to_notify.append(partner.id)

    def _process_followers_for_invoice(self, params):
        """Traite les abonnements et désabonnements selon le type de facture."""
        partners_to_notify = []

        if self.move_type == 'out_invoice':
            self._subscribe_partner_if_needed(
                self.create_uid.partner_id,
                params['follow']['inv_creator'],
                params['notify']['inv_creator'],
                partners_to_notify,
            )
            self._subscribe_partner_if_needed(
                self.user_id.partner_id,
                params['follow']['inv_seller'],
                params['notify']['inv_seller'],
                partners_to_notify,
            )
            self._subscribe_partner_if_needed(
                self.partner_id,
                params['follow'].get('entry_customer'),
                params['notify']['entry_customer'],
                partners_to_notify,
            )
            self._remove_followers_out_invoice(params)

        elif self.move_type == 'in_invoice':
            self._subscribe_partner_if_needed(
                self.create_uid.partner_id,
                params['follow']['bill_creator'],
                params['notify']['bill_creator'],
                partners_to_notify,
            )
            self._subscribe_partner_if_needed(
                self.user_id.partner_id,
                params['follow']['bill_purrep'],
                params['notify']['bill_purrep'],
                partners_to_notify,
            )
            self._subscribe_partner_if_needed(
                self.partner_id,
                params['follow']['entry_customer'],
                params['notify']['entry_customer'],
                partners_to_notify,
            )
            self._remove_followers_in_invoice(params)

        elif self.move_type == 'entry':
            self._subscribe_partner_if_needed(
                self.create_uid.partner_id,
                params['follow']['entry_creator'],
                params['notify']['entry_creator'],
                partners_to_notify,
            )
            self._subscribe_partner_if_needed(
                self.user_id.partner_id,
                params['follow']['entry_salerep'],
                params['notify']['entry_salerep'],
                partners_to_notify,
            )
            self._subscribe_partner_if_needed(
                self.partner_id,
                params['follow']['entry_customer'],
                params['notify']['entry_customer'],
                partners_to_notify,
            )
            self._remove_followers_entry(params)

        return partners_to_notify

    def _remove_followers_out_invoice(self, params):
        """Retire les abonnés non autorisés pour les factures clients."""
        if not self.message_follower_ids or not self.partner_id:
            return

        follower_to_remove_ids = self.env['mail.followers']
        for follower in self.message_follower_ids:
            if follower.partner_id.id == self.partner_id.id and not params['follow'].get(
                'entry_customer', params['follow'].get('inv_customer')
            ):
                follower_to_remove_ids += follower
            if (
                follower.partner_id.id in [self.user_id.partner_id.id, self.invoice_user_id.partner_id.id]
            ) and not params['follow']['inv_seller']:
                follower_to_remove_ids += follower
            if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow'].get('inv_creator'):
                follower_to_remove_ids += follower

        if follower_to_remove_ids:
            self.message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

    def _remove_followers_in_invoice(self, params):
        """Retire les abonnés non autorisés pour les factures fournisseurs."""
        if not self.message_follower_ids or not self.partner_id:
            return

        follower_to_remove_ids = self.env['mail.followers']
        for follower in self.message_follower_ids:
            if follower.partner_id.id == self.partner_id.id and not params['follow'].get('entry_customer'):
                follower_to_remove_ids += follower
            if follower.partner_id.id == self.user_id.partner_id.id and not params['follow']['bill_purrep']:
                follower_to_remove_ids += follower
            if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow'].get('bill_creator'):
                follower_to_remove_ids += follower

        if follower_to_remove_ids:
            self.message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

    def _remove_followers_entry(self, params):
        """Retire les abonnés non autorisés pour les écritures comptables."""
        if not self.message_follower_ids or not self.partner_id:
            return

        follower_to_remove_ids = self.env['mail.followers']
        for follower in self.message_follower_ids:
            if follower.partner_id.id == self.partner_id.id and not params['follow']['entry_customer']:
                follower_to_remove_ids += follower
            if follower.partner_id.id == self.user_id.partner_id.id and not params['follow']['entry_salerep']:
                follower_to_remove_ids += follower
            if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow'].get('entry_creator'):
                follower_to_remove_ids += follower

        if follower_to_remove_ids:
            self.message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

    @api.model_create_multi
    def create(self, vals_list):
        invoices = super(
            E3KAccountMove, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).create(vals_list)

        params = self._get_notification_params()

        for invoice in invoices:
            partners_to_notify = invoice._process_followers_for_invoice(params)
            invoice._e3k_notify_partners(partners_to_notify)

        return invoices

    def write(self, vals):
        super(
            E3KAccountMove, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).write(vals)

        params = self._get_notification_params()

        for invoice in self:
            partners_to_notify = invoice._process_followers_for_invoice(params)
            invoice._e3k_notify_partners(partners_to_notify)
