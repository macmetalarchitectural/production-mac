# -*- coding: utf-8 -*-

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def action_send_mail(self):
        for wizard in self:
            if (
                wizard.composition_mode == "comment"
                and wizard.res_model
                and wizard.res_id
                and wizard.partner_ids
            ):
                try:
                    document = self.env[wizard.res_model].browse(wizard.res_id)
                    if document.exists() and hasattr(document, "message_subscribe"):
                        document.message_subscribe(partner_ids=wizard.partner_ids.ids)
                        _logger.info(
                            "Subscribed partners %s to %s(%s)",
                            wizard.partner_ids.ids,
                            wizard.res_model,
                            wizard.res_id,
                        )
                except Exception as e:
                    _logger.warning(
                        "Failed to subscribe partners to %s(%s): %s",
                        wizard.res_model,
                        wizard.res_id,
                        e,
                    )
        return super().action_send_mail()
