# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class send_payment_notification(models.TransientModel):
    _name = "send.payment.notification"
    _description = "Send Payment Notification"

    partner_ids = fields.Many2many('res.partner', 'payment_notification_partner_rel', 'notification_id', 'payment_id',
                                   string="Partners", copy=False)

    def send_message_view(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        dont_have_email = ""
        for payment in self.env['account.payment'].browse(active_ids):
            if not payment.partner_id.email:
                dont_have_email += payment.partner_id.name + ".\n"
        if dont_have_email:
            raise UserError(_("""These partners do not have an email address: \n """ + dont_have_email))

        template = self.env.ref('e3k_advanced_payment.email_template_payment_notification', False)
        for payment in self.env['account.payment'].browse(active_ids):
            message_vals = {
                'composition_mode': 'comment',
                'mass_mailing_name': False,
                'use_active_domain': False,
                'attachment_ids': [],
                'template_id': template and template.id or False,
                'body': '<p>TEST<>',
                'is_log': False,
                'mail_server_id': False,
                'parent_id': False,
                'mass_mailing_campaign_id': False,
                'notify': False,
                'no_auto_thread': True,
                'reply_to': self.env.user.email or '',
                'model': 'account.payment',
                'partner_ids': [[6, False, [payment.partner_id.id]]],
                'res_id': payment.id,
                'email_from': payment.partner_id.name + '<' + payment.partner_id.name + '>',
                'subject': payment.company_id.name + 'Payment + (Ref ' + payment.name or 'n/a' + ')'
            }
            new_message = self.env['mail.compose.message'].create(message_vals)
            update_values = \
                self.env['mail.compose.message'].onchange_template_id(template.id, 'comment', 'account.payment',
                                                                      payment.id)['value']
            new_message.write(update_values)
            new_message.send_mail_action()
        return True
