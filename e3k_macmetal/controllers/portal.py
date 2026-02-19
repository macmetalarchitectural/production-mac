# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from datetime import datetime, timedelta
from pytz import timezone, UTC

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.portal.controllers import portal

class CustomerPortal(portal.CustomerPortal):

  @http.route(['/my/orders/<int:order_id>/accept'], type='jsonrpc', auth="public", website=True)
  def portal_quote_accept(self, order_id, access_token=None, delivery=None, name=None, signature=None):
    # get from query string if not on json param
    access_token = access_token or request.httprequest.args.get('access_token')
    try:
      order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
    except (AccessError, MissingError):
      return {'error': _('Invalid order.')}

    if not order_sudo._has_to_be_signed():
      return {'error': _('The order is not in a state requiring customer signature.')}
    if not signature:
      return {'error': _('Signature is missing.')}
    if not name:
      return {'error': _('Name is missing.')}
    if not delivery:
      return {'error': _('Delivery is missing.')}

    try:
      order_sudo.write({
        'commitment_date': delivery,
        'customer_delivery_date': delivery,
        'signed_by': name,
        'signed_on': fields.Datetime.now(),
        'signature': signature,
      })
      # flush now to make signature data available to PDF render request
      request.env.cr.flush()
    except (TypeError, binascii.Error) as e:
      return {'error': _('Invalid signature data.')}

    if not order_sudo._has_to_be_paid():
      order_sudo._validate_order()

    pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [order_sudo.id])[0]

    # In Odoo 19, use message_post directly instead of _message_post_helper
    order_sudo.message_post(
      attachments=[('%s.pdf' % order_sudo.name, pdf)],
      author_id=(
        order_sudo.partner_id.id
        if request.env.user._is_public()
        else request.env.user.partner_id.id
      ),
      body=_('Order signed by %s', name),
      message_type='comment',
      subtype_xmlid='mail.mt_comment',
    )

    query_string = '&message=sign_ok'
    if order_sudo._has_to_be_paid():
      query_string += '&allow_payment=yes'
    return {
      'force_refresh': True,
      'redirect_url': order_sudo.get_portal_url(query_string=query_string),
    }

  @http.route(['/get_padding_delivery_days'], type='json', auth="public",) #website=True)
  def get_padding_delivery_days(self):
    company = request.env.company
    return company.padding_delivery_days
