# -*- coding: utf-8 -*-
from odoo import api, models


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_notification_params(self, state='quotation'):
        """Récupère les paramètres de configuration pour les notifications et abonnements."""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        if state == 'confirmed':
            prefix = 'po'
        else:  # quotation
            prefix = 'req_quo'

        return {
            'follow': {
                'creator': IrConfigParameter.get_param(f'{prefix}_creator_follow'),
                'purrep': IrConfigParameter.get_param(f'{prefix}_purrep_follow'),
                'vendor': IrConfigParameter.get_param(f'{prefix}_vendor_follow'),
            },
            'notify': {
                'creator': str2bool(IrConfigParameter.get_param(f'{prefix}_creator_notify')),
                'purrep': str2bool(IrConfigParameter.get_param(f'{prefix}_purrep_notify')),
                'vendor': str2bool(IrConfigParameter.get_param(f'{prefix}_vendor_notify')),
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

    def _process_followers_for_purchase(self, params):
        """Traite les abonnements et désabonnements pour les commandes d'achat."""
        partners_to_notify = []

        # Abonnements
        self._subscribe_partner_if_needed(
            self.create_uid.partner_id, params['follow']['creator'], params['notify']['creator'], partners_to_notify
        )
        self._subscribe_partner_if_needed(
            self.user_id.partner_id, params['follow']['purrep'], params['notify']['purrep'], partners_to_notify
        )
        self._subscribe_partner_if_needed(
            self.partner_id, params['follow']['vendor'], params['notify']['vendor'], partners_to_notify
        )

        # Désabonnements
        if self.message_follower_ids and self.partner_id:
            follower_to_remove_ids = self.env['mail.followers']
            for follower in self.message_follower_ids:
                if follower.partner_id.id == self.partner_id.id and not params['follow']['vendor']:
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.user_id.partner_id.id and not params['follow']['purrep']:
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow']['creator']:
                    follower_to_remove_ids += follower

            if follower_to_remove_ids:
                follower_to_remove_ids._invalidate_documents()
                self.message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

        return partners_to_notify

    def button_confirm(self):
        params = self._get_notification_params(state='confirmed')

        ignore_subscribers = []
        if not params['follow']['vendor']:
            ignore_subscribers.append(self.partner_id.id)
        if not params['follow']['purrep']:
            ignore_subscribers.append(self.user_id.partner_id.id)
        if not params['follow']['creator']:
            ignore_subscribers.append(self.create_uid.partner_id.id)

        result = super(E3KPurchaseOrder, self.with_context(e3k_ignore_subscribers=ignore_subscribers)).button_confirm()

        partners_to_notify = self._process_followers_for_purchase(params)
        self._e3k_notify_partners(partners_to_notify)

        return result

    @api.model_create_multi
    def create(self, vals_list):
        purchases = super(
            E3KPurchaseOrder, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).create(vals_list)

        params = self._get_notification_params(state='quotation')

        for purchase in purchases:
            partners_to_notify = purchase._process_followers_for_purchase(params)
            purchase._e3k_notify_partners(partners_to_notify)

        return purchases
