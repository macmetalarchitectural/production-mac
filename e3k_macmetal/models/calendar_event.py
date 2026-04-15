# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import api, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def _get_contact_details_description(self, organizer, partners):
        """Override to prevent Odoo from automatically appending organizer
        and contact partner details to the calendar event description.
        """
        return Markup("")
