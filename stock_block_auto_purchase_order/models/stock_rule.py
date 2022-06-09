# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields, SUPERUSER_ID, _
from collections import defaultdict
from odoo.addons.purchase.models.purchase import PurchaseOrder
from odoo.tools import float_compare
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import groupby
from odoo.addons.stock.models.stock_rule import ProcurementException

from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockRule(models.Model):
    _inherit = "stock.rule"

    def block_po_purchaceorder(self, procurements):
        procurements_by_po_domain = defaultdict(list)
        errors = []
        for procurement, rule in procurements:
            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])

            supplier = False
            if procurement.values.get('supplierinfo_id'):
                supplier = procurement.values['supplierinfo_id']
            else:
                supplier = procurement.product_id.with_company(procurement.company_id.id)._select_seller(
                    partner_id=procurement.values.get("supplierinfo_name"),
                    quantity=procurement.product_qty,
                    date=procurement_date_planned.date(),
                    uom_id=procurement.product_uom)

            # Fall back on a supplier for which no price may be defined. Not ideal, but better than
            # blocking the user.
            supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (
                          procurement.product_id.display_name)
                errors.append((procurement, msg))

            partner = supplier.name
            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            procurements_by_po_domain[domain].append((procurement, rule))

        if errors:
            raise ProcurementException(errors)

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = False
            company_id = procurements[0].company_id

            for procurement in procurements:
                # raise UserError('procurements %s' % str(procurement))
                positive_values = [p.values for p in procurements if
                                   float_compare(p.product_qty, 0.0, precision_rounding=p.product_uom.rounding) >= 0]
                if positive_values:
                    # We need a rule to generate the PO. However the rule generated
                    # the same domain for PO and the _prepare_purchase_order method
                    # should only uses the common rules's fields.
                    vals = rules[0]._prepare_purchase_order(company_id, origins, positive_values)
                    # The company_id is the same for all procurements since
                    # _make_po_get_domain add the company in the domain.
                    # We use SUPERUSER_ID since we don't want the current user to be follower of the PO.
                    # Indeed, the current user may be a user without access to Purchase, or even be a portal user.
                    vals['block_auto_purchase_order'] = True
                    po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)

                po_lines_by_product = {}
                grouped_po_lines = groupby(
                    po.order_line.filtered(
                        lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(
                        lambda l: l.product_id.id), key=lambda l: l.product_id.id)

                for product, po_lines in grouped_po_lines:
                    po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))

                po_line_values = []

                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if float_compare(procurement.product_qty, 0,
                                 precision_rounding=procurement.product_uom.rounding) <= 0:
                    # If procurement contains negative quantity, don't create a new line that would contain negative qty
                    continue
                # If it does not exist a PO line for current procurement.
                # Generate the create values for it and add it to a list in
                # order to create it in batch.
                partner = procurement.values['supplier'].name

                po_line_values.append(self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                    procurement.product_id, procurement.product_qty,
                    procurement.product_uom, procurement.company_id,
                    procurement.values, po))
                # Check if we need to advance the order date for the new line
                order_date_planned = procurement.values['date_planned'] - relativedelta(
                    days=procurement.values['supplier'].delay)
                if fields.Date.to_date(order_date_planned) < fields.Date.to_date(po.date_order):
                    po.date_order = order_date_planned

                self.env['purchase.order.line'].sudo().create(po_line_values)

    def unique_po_purchaceorder(self, procurements):
        procurements_by_po_domain = defaultdict(list)
        errors = []
        for procurement, rule in procurements:

            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])

            supplier = False
            if procurement.values.get('supplierinfo_id'):
                supplier = procurement.values['supplierinfo_id']
            else:
                supplier = procurement.product_id.with_company(procurement.company_id.id)._select_seller(
                    partner_id=procurement.values.get("supplierinfo_name"),
                    quantity=procurement.product_qty,
                    date=procurement_date_planned.date(),
                    uom_id=procurement.product_uom)

            # Fall back on a supplier for which no price may be defined. Not ideal, but better than
            # blocking the user.
            supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (
                          procurement.product_id.display_name)
                errors.append((procurement, msg))

            partner = supplier.name
            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            procurements_by_po_domain[domain].append((procurement, rule))

        if errors:
            raise ProcurementException(errors)

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            domain += (('origin', '=', str(origins).replace('{', '').replace('}', '')),)
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            # raise UserError('domain %s' % str(domain))
            company_id = procurements[0].company_id
            if not po:
                positive_values = [p.values for p in procurements if
                                   float_compare(p.product_qty, 0.0, precision_rounding=p.product_uom.rounding) >= 0]
                if positive_values:
                    # We need a rule to generate the PO. However the rule generated
                    # the same domain for PO and the _prepare_purchase_order method
                    # should only uses the common rules's fields.
                    vals = rules[0]._prepare_purchase_order(company_id, origins, positive_values)
                    # The company_id is the same for all procurements since
                    # _make_po_get_domain add the company in the domain.
                    # We use SUPERUSER_ID since we don't want the current user to be follower of the PO.
                    # Indeed, the current user may be a user without access to Purchase, or even be a portal user.
                    vals['unique_purchase_order'] = True
                    po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)
            else:
                # If a purchase order is found, adapt its `origin` field.
                if po.origin:
                    missing_origins = origins - set(po.origin.split(', '))
                    if missing_origins:
                        po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
                else:
                    po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(
                po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(
                    lambda l: l.product_id.id), key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                                                            procurement.product_qty, procurement.product_uom,
                                                            company_id,
                                                            procurement.values, po_line)
                    po_line.write(vals)
                else:
                    if float_compare(procurement.product_qty, 0,
                                     precision_rounding=procurement.product_uom.rounding) <= 0:
                        # If procurement contains negative quantity, don't create a new line that would contain negative qty
                        continue
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].name
                    po_line_values.append(self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
                    # Check if we need to advance the order date for the new line
                    order_date_planned = procurement.values['date_planned'] - relativedelta(
                        days=procurement.values['supplier'].delay)
                    if fields.Date.to_date(order_date_planned) < fields.Date.to_date(po.date_order):
                        po.date_order = order_date_planned
            self.env['purchase.order.line'].sudo().create(po_line_values)

    def _run_buy(self, procurements):
        result = False

        vals = {}

        for procurement, rule in procurements:
            group_id = procurement.values.get('group_id')

            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])

            supplier = False
            if procurement.values.get('supplierinfo_id'):
                supplier = procurement.values['supplierinfo_id']
            else:
                supplier = procurement.product_id.with_company(procurement.company_id.id)._select_seller(
                    partner_id=procurement.values.get("supplierinfo_name"),
                    quantity=procurement.product_qty,
                    date=procurement_date_planned.date(),
                    uom_id=procurement.product_uom)

            # Fall back on a supplier for which no price may be defined. Not ideal, but better than
            # blocking the user.
            supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (
                          procurement.product_id.display_name)
                errors.append((procurement, msg))

            partner = supplier.name

            # sale_order_line = self.env['sale.order.line'].search([('order_id', '=', group_id.sale_id.id), ('product_id', '=', procurement.product_id.id)])
            # sale_order_line.filtered(lambda sol: sol.old_product_uom_qty != sol.product_uom_qty and sol.product_id == procurement.product_id.id)

            #sale_order_line = group_id.sale_id.order_line.filtered(lambda sol: sol.old_product_uom_qty != sol.product_uom_qty and sol.product_id == procurement.product_id.id)

            if partner.id in vals:
                vals[partner.id]['block_auto_purchase_order'] = partner.block_auto_purchase_order
                vals[partner.id]['unique_purchase_order'] = partner.unique_purchase_order
                vals[partner.id]['new_sale_order'] = False if group_id.sale_id.purchase_order_count else True
                vals[partner.id]['sale_order_id'] = group_id.sale_id
                #vals[partner.id]['old_product_uom_qty'] = sale_order_line.old_product_uom_qty
                vals[partner.id]['values'].append((procurement, rule))
            else:
                procurement_by_partner = []
                procurement_by_partner.append((procurement, rule))
                vals[partner.id] = {'block_auto_purchase_order': partner.block_auto_purchase_order,
                                    'unique_purchase_order': partner.unique_purchase_order,
                                    'new_sale_order': False if group_id.sale_id.purchase_order_count else True,
                                    'sale_order_id': group_id.sale_id,
                                    #'old_product_uom_qty': sale_order_line.old_product_uom_qty,
                                    'values': procurement_by_partner
                                    }

        for val_key in vals.keys():
            partner_id = self.env['res.partner'].search([('id', '=', val_key)])

            result = False

            if partner_id.block_auto_purchase_order:
                # appliquer le scenario block_po
                if vals[val_key]['new_sale_order']:
                    result = self.block_po_purchaceorder(vals[val_key]['values'])
            elif partner_id.unique_purchase_order:
                # appliquer le scenario unique_po
                if vals[val_key]['new_sale_order']:
                    result = self.unique_po_purchaceorder(vals[val_key]['values'])
            else:
                # appliquer le scenario natif odoo
                result = super(StockRule, self)._run_buy(vals[val_key]['values'])

        return result

# class SaleOrder(models.Model):
#     _inherit = "sale.order.line"
#
#     old_product_uom_qty = fields.Float(string='Old Quantity', digits='Product Unit of Measure', default=1.0)
#
#     def write(self, vals):
#         if 'product_uom_qty' in vals:
#             vals['old_product_uom_qty'] = self.product_uom_qty
#
#         return super(SaleOrder, self).write(vals)