# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
          self.update({
            'partner_invoice_id': False,
            'fiscal_position_id': False,
          })
          return
  
        self = self.with_company(self.company_id)
  
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
          'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
          'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
          'partner_invoice_id': addr['invoice'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
          user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
          values['user_id'] = user_id
  
        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms'):
          if self.terms_type == 'html' and self.env.company.invoice_terms_html:
            baseurl = html_keep_url(self.get_base_url() + '/terms')
            values['note'] = _('Terms & Conditions: %s', baseurl)
          elif not is_html_empty(self.env.company.invoice_terms):
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
          default_team = self.env.context.get('default_team_id', False) or self.partner_id.team_id.id
          values['team_id'] = self.env['crm.team'].with_context(
            default_team_id=default_team
          )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)],
                                 user_id=user_id)
        self.update(values)
