# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from datetime import datetime, timedelta
from pytz import timezone, UTC

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager

class CustomerPortal(portal.CustomerPortal):

  @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
  def portal_quote_accept(self, order_id, access_token=None, delivery=None, name=None, signature=None):
    # get from query string if not on json param
    access_token = access_token or request.httprequest.args.get('access_token')
    try:
      order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
    except (AccessError, MissingError):
      return {'error': _('Invalid order.')}

    if not order_sudo.has_to_be_signed():
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
      request.env.cr.commit()
    except (TypeError, binascii.Error) as e:
      return {'error': _('Invalid signature data.')}

    if not order_sudo.has_to_be_paid():
      order_sudo.action_confirm()
      order_sudo._send_order_confirmation_mail()

    pdf = request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[0]

    _message_post_helper(
      'sale.order', order_sudo.id, _('Order signed by %s') % (name,),
      attachments=[('%s.pdf' % order_sudo.name, pdf)],
      **({'token': access_token} if access_token else {}))

    query_string = '&message=sign_ok'
    if order_sudo.has_to_be_paid(True):
      query_string += '#allow_payment=yes'
    return {
      'force_refresh': True,
      'redirect_url': order_sudo.get_portal_url(query_string=query_string),
    }

  @http.route(['/get_padding_delivery_days'], type='json', auth="public",) #website=True)
  def get_padding_delivery_days(self):
    company = request.env.company
    return company.padding_delivery_days