import logging

from odoo import SUPERUSER_ID, models

_logger = logging.getLogger(__name__)


class E3KMailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _e3k_notify_partners(self, partners_to_notify):
        # Remove duplication if any to avoid double notifications
        partners_to_notify = sorted(set(partners_to_notify))
        current_partner = self.env.user.partner_id

        for partner_id in partners_to_notify:
            if not partner_id:
                _logger.warning('Skipping notification for invalid partner_id: %s', partner_id)
                continue
            partner = self.env['res.partner'].browse(partner_id)

            if partner == current_partner:
                self_send = self.with_user(SUPERUSER_ID)
            else:
                self_send = self

            if 'project_id' in self._fields:
                e3k_user_name = self.project_id.user_id.sudo().name
            else:
                e3k_user_name = partner.name

            self_send.with_context(
                mail_auto_subscribe_no_notify=False,
                e3k_user_name=e3k_user_name,
            )._message_auto_subscribe_notify([partner_id], 'e3k_notifications_management.message_user_assigned')

    def _message_subscribe(self, partner_ids=None, subtype_ids=None, customer_ids=None):
        e3k_ignore_subscribers = self.env.context.get('e3k_ignore_subscribers', [])
        if e3k_ignore_subscribers:
            partner_ids = [p for p in partner_ids if p not in e3k_ignore_subscribers]
            if not partner_ids:
                return True
        return super(E3KMailThread, self)._message_subscribe(partner_ids, subtype_ids, customer_ids)
