# -*- coding: utf-8 -*-
from odoo import api, models


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KSaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_notification_params(self, state='quotation'):
        """Récupère les paramètres de configuration pour les notifications et abonnements."""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        if state == 'confirmed':
            prefix = 'so'
        else:  # quotation
            prefix = 'quo'

        return {
            'follow': {
                'creator': IrConfigParameter.get_param(f'{prefix}_creator_follow'),
                'salerep': IrConfigParameter.get_param(f'{prefix}_salerep_follow'),
                'customer': IrConfigParameter.get_param(f'{prefix}_customer_follow'),
            },
            'notify': {
                'creator': str2bool(IrConfigParameter.get_param(f'{prefix}_creator_notify')),
                'salerep': str2bool(IrConfigParameter.get_param(f'{prefix}_salerep_notify')),
                'customer': str2bool(IrConfigParameter.get_param(f'{prefix}_customer_notify')),
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

    def _process_followers_for_sale(self, params):
        """Traite les abonnements et désabonnements pour les commandes de vente."""
        partners_to_notify = []

        # Abonnements
        self._subscribe_partner_if_needed(
            self.create_uid.partner_id, params['follow']['creator'], params['notify']['creator'], partners_to_notify
        )
        self._subscribe_partner_if_needed(
            self.user_id.partner_id, params['follow']['salerep'], params['notify']['salerep'], partners_to_notify
        )
        self._subscribe_partner_if_needed(
            self.partner_id, params['follow']['customer'], params['notify']['customer'], partners_to_notify
        )

        # Désabonnements
        if self.message_follower_ids and self.partner_id:
            follower_to_remove_ids = self.env['mail.followers']
            for follower in self.message_follower_ids:
                if follower.partner_id.id == self.partner_id.id and not params['follow']['customer']:
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.user_id.partner_id.id and not params['follow']['salerep']:
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow']['creator']:
                    follower_to_remove_ids += follower

            if follower_to_remove_ids:
                self.sudo().message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

        return partners_to_notify

    def action_confirm(self):
        params = self._get_notification_params(state='confirmed')

        ignore_subscribers = []
        if not params['follow']['customer']:
            ignore_subscribers.append(self.partner_id.id)
        if not params['follow']['salerep']:
            ignore_subscribers.append(self.user_id.partner_id.id)
        if not params['follow']['creator']:
            ignore_subscribers.append(self.create_uid.partner_id.id)

        result = super(E3KSaleOrder, self.with_context(e3k_ignore_subscribers=ignore_subscribers)).action_confirm()

        partners_to_notify = self._process_followers_for_sale(params)
        self._e3k_notify_partners(partners_to_notify)

        return result

    @api.model_create_multi
    def create(self, vals_list):
        sales = super(
            E3KSaleOrder, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).create(vals_list)

        params = self._get_notification_params(state='quotation')

        for sale in sales:
            partners_to_notify = sale._process_followers_for_sale(params)
            sale._e3k_notify_partners(partners_to_notify)

        return sales
