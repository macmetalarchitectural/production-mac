# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KStockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_notification_params(self):
        """Récupère les paramètres de configuration pour les notifications et abonnements."""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        return {
            'follow': {
                'creator': IrConfigParameter.get_param('picking_creator_follow'),
                'salerep': IrConfigParameter.get_param('picking_salerep_follow'),
                'customer': IrConfigParameter.get_param('picking_customer_follow'),
            },
            'notify': {
                'creator': str2bool(IrConfigParameter.get_param('picking_creator_notify')),
                'salerep': str2bool(IrConfigParameter.get_param('picking_salerep_notify')),
                'customer': str2bool(IrConfigParameter.get_param('picking_customer_notify')),
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

    def _process_followers_for_picking(self, params):
        """Traite les abonnements et désabonnements pour les picking."""
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
        if self.message_follower_ids:
            follower_to_remove_ids = self.env['mail.followers']
            for follower in self.message_follower_ids:
                if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow']['creator']:
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.partner_id.id and not params['follow']['customer']:
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.user_id.partner_id.id and not params['follow']['salerep']:
                    follower_to_remove_ids += follower

            if follower_to_remove_ids:
                self.message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

        return partners_to_notify

    @api.model_create_multi
    def create(self, vals_list):
        pickings = super(
            E3KStockPicking, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).create(vals_list)

        params = self._get_notification_params()

        for picking in pickings:
            partners_to_notify = picking._process_followers_for_picking(params)
            if partners_to_notify:
                picking._e3k_notify_partners(partners_to_notify)

        return pickings

    def write(self, values):
        picking = super(
            E3KStockPicking, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).write(values)

        params = self._get_notification_params()

        for rec in self:
            partners_to_notify = rec._process_followers_for_picking(params)
            if partners_to_notify:
                rec._e3k_notify_partners(partners_to_notify)

        return picking
