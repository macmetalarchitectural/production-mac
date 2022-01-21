# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_sale_note_terms(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'e3k_default_reports.use_sale_order_terms') and self.env.company.sale_order_terms or ''

    sale_note_termes = fields.Text('Terms and conditions', default=_default_sale_note_terms)

    def _compute_print_default_code(self):
        return self.env['ir.config_parameter'] \
                   .sudo().get_param('e3k_default_reports.add_default_code_report') or False


class AccountMove(models.Model):
    _inherit = 'account.move'

    print_ordered_qty = fields.Boolean('print ordedred qty', compute="_compute_print_ordered_qty", store=True)
    print_delivered_qty = fields.Boolean('print Delivered qty', compute="_compute_print_delivered_qty", store=True)

    def _compute_print_ordered_qty(self):
        for rec in self:
            rec.print_ordered_qty = self.env['ir.config_parameter'] \
                                        .sudo().get_param('e3k_default_reports.add_ordered_qty_in_report') or False

    def _compute_print_delivered_qty(self):
        for rec in self:
            rec.print_delivered_qty = self.env['ir.config_parameter'] \
                                          .sudo().get_param('e3k_default_reports.add_qty_delivered_in_report') or False

    def _compute_print_default_code(self):
        return self.env['ir.config_parameter'] \
                   .sudo().get_param('e3k_default_reports.add_default_code_report') or False

    def _compute_add_default_sale_description(self):
        print("sale description")
        print(self.env['ir.config_parameter'] \
              .sudo().get_param('e3k_default_reports._compute_add_default_sale_description'))
        return self.env['ir.config_parameter'] \
                   .sudo().get_param('e3k_default_reports.add_default_sale_description') or False

    def has_so_or_po(self):
        for rec in self:
            default_value = False
            for line in rec.invoice_line_ids:
                if line.purchase_line_id or line.sale_line_ids:
                    default_value = True
                    break
                else:
                    default_value = False
            return default_value


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def ge_commanded_qty(self):
        for rec in self:
            qty = 0
            if rec.purchase_line_id:
                qty = rec.purchase_line_id.product_uom_qty
            else:
                for sale_line in rec.sale_line_ids:
                    qty = qty + sale_line.product_uom_qty

    def _get_computed_name(self):
        self.ensure_one()
        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        # if product.partner_ref:
        #     values.append(product.partner_ref)
        if self.product_id:
            values.append(self.product_id.name)
        # if self.journal_id.type == 'sale':
        #     if product.description_sale:
        #         print(product.description_sale)
        #         values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                print(product.description_purchase)
                values.append(product.description_purchase)
        print('\n'.join(values))
        return '\n'.join(values)

    def ge_commanded_qty_delivered_received(self):
        for rec in self:
            qty_delivered_received = 0
            if rec.purchase_line_id:
                qty_delivered_received = rec.purchase_line_id.qty_received
            else:
                for sale_line in rec.sale_line_ids:
                    qty_delivered_received = qty_delivered_received + sale_line.qty_delivered

            return qty_delivered_received

    def ge_commanded_qty_invoiced(self):
        for rec in self:
            qty_invoiced = 0
            if rec.purchase_line_id or rec.sale_line_ids:
                if rec.purchase_line_id:
                    qty_invoiced = rec.purchase_line_id.qty_invoiced
                else:
                    for sale_line in rec.sale_line_ids:
                        qty_invoiced = qty_invoiced + sale_line.qty_invoiced
            else:
                qty_invoiced = rec.quantity

            return qty_invoiced

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)

    def name_get(self):
        result = []
        for so_line in self.sudo():
            # name = '%s - %s' % (so_line.order_id.name, so_line.name and so_line.name.split('\n')[0] or so_line.product_id.name)
            # if so_line.order_partner_id.ref:
            #     name = '%s (%s)' % (name, so_line.order_partner_id.ref)
            name = so_line.product_id.name
            result.append((so_line.id, name))
        return result

    def get_sale_order_line_multiline_description_sale(self, product):
        return product.name


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)


class ResCompany(models.Model):
    _inherit = "res.company"

    b_logo = fields.Binary(string="Becorp Logo", readonly=False)
    sale_order_terms = fields.Text(string='Default Sale Terms and Conditions', translate=True)
