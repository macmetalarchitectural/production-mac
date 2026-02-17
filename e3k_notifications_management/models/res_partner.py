import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KResPartner(models.Model):
    _inherit = "res.partner"

    user_id = fields.Many2one(tracking=False)  # no-check

    def _get_notification_params(self):
        """Récupère les paramètres de configuration pour les notifications et abonnements."""
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        return {
            'follow': {
                'creator': IrConfigParameter.get_param('cont_creator_follow'),
                'salerep': IrConfigParameter.get_param('cont_salerep_follow'),
                'customer': IrConfigParameter.get_param('cont_customer_follow'),
            },
            'notify': {
                'creator': str2bool(IrConfigParameter.get_param('cont_creator_notify')),
                'salerep': str2bool(IrConfigParameter.get_param('cont_salerep_notify')),
                'customer': str2bool(IrConfigParameter.get_param('cont_customer_notify')),
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

    def _process_followers_for_contact(self, params):
        """Traite les abonnements et désabonnements pour les contacts/partenaires."""
        partners_to_notify = []

        # Abonnements
        if self.user_id:
            self._subscribe_partner_if_needed(
                self.user_id.partner_id, params['follow']['salerep'], params['notify']['salerep'], partners_to_notify
            )

        self._subscribe_partner_if_needed(
            self.create_uid.partner_id, params['follow']['creator'], params['notify']['creator'], partners_to_notify
        )

        # Abonner les enfants (contacts) si activé
        if params['follow']['customer']:
            for child in self.child_ids:
                follower_partner_ids = self.message_follower_ids.mapped('partner_id').ids
                if child.id not in follower_partner_ids or not self.message_follower_ids:
                    self.with_context(mail_auto_subscribe_no_notify=True).message_subscribe([child.id])
                    if params['notify']['customer']:
                        partners_to_notify.append(child.id)

        # Désabonnements
        if self.message_follower_ids:
            follower_to_remove_ids = self.env['mail.followers']
            for follower in self.message_follower_ids:
                if (
                    self.user_id
                    and follower.partner_id.id == self.user_id.partner_id.id
                    and not params['follow']['salerep']
                ):
                    follower_to_remove_ids += follower
                if follower.partner_id.id == self.create_uid.partner_id.id and not params['follow']['creator']:
                    follower_to_remove_ids += follower

            if follower_to_remove_ids:
                self.message_unsubscribe(follower_to_remove_ids.mapped('partner_id').ids)

        return partners_to_notify

    @api.model_create_multi
    def create(self, vals_list):
        contacts = super(
            E3KResPartner, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).create(vals_list)

        params = self._get_notification_params()

        for contact in contacts:
            partners_to_notify = contact._process_followers_for_contact(params)
            contact._e3k_notify_partners(partners_to_notify)

        return contacts

    def write(self, values):
        contact = super(
            E3KResPartner, self.with_context(mail_create_nosubscribe=True, mail_auto_subscribe_no_notify=True)
        ).write(values)

        params = self._get_notification_params()
        partners_to_notify = []

        for rec in self:
            partners_to_notify.extend(rec._process_followers_for_contact(params))

        self._e3k_notify_partners(partners_to_notify)
        return contact
