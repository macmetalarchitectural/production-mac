# -*- coding: utf-8 -*-

import json
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _subscribe_partners_to_document(self):
        for wizard in self:
            if (
                wizard.composition_mode == "comment"
                and wizard.model
                and wizard.res_ids
                and wizard.partner_ids
            ):
                res_ids = wizard.res_ids
                if isinstance(res_ids, str):
                    res_ids = json.loads(res_ids)
                document = self.env[wizard.model].browse(res_ids)
                if document.exists() and hasattr(document, "message_subscribe"):
                    document.message_subscribe(partner_ids=wizard.partner_ids.ids)
                    _logger.info(
                        "Subscribed partners %s to %s(%s)",
                        wizard.partner_ids.ids,
                        wizard.model,
                        wizard.res_ids,
                    )

    def action_send_mail(self):
        self._subscribe_partners_to_document()
        return super().action_send_mail()
