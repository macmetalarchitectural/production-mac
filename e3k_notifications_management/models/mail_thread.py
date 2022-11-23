from odoo import models, SUPERUSER_ID


class E3KMailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _e3k_notify_partners(self, partners_to_notify):
        # Remove duplication if any to avoid double notifications
        partners_to_notify = sorted(set(partners_to_notify))
        current_partner = self.env.user.partner_id

        for partner_id in partners_to_notify:
            partner = self.env['res.partner'].browse(partner_id)

            if partner == current_partner:
                self_send = self.with_user(SUPERUSER_ID)
            else:
                self_send = self

            if partner_id:
                self_send.with_context(
                    mail_auto_subscribe_no_notify=False,
                    e3k_user_name=partner.name,
                )._message_auto_subscribe_notify(
                    [partner_id], 'e3k_notifications_management.message_user_assigned'
                )

