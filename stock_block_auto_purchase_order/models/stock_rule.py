# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _, Command
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.tools import groupby as odoo_groupby

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    def block_po_purchaceorder(self, procurements):
        """Crée un nouveau PO pour chaque procurement, sans jamais consolider."""
        procurements_by_po_domain = defaultdict(list)
        errors = []

        for procurement, rule in procurements:
            company_id = rule.company_id or procurement.company_id

            supplier = rule._get_matching_supplier(
                procurement.product_id, procurement.product_qty, procurement.product_uom,
                company_id, procurement.values,
            )

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s '
                    '(no vendor defined, minimum quantity not reached, dates not valid, ...). '
                    'Go on the product form and complete the list of vendors.',
                    procurement.product_id.display_name,
                )
                errors.append((procurement, msg))
                continue

            procurement.values['supplier'] = supplier
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(company_id, procurement.values, supplier.partner_id)
            procurements_by_po_domain[domain].append((procurement, rule))

        if errors:
            raise ProcurementException(errors)

        for domain, procurements_rules in procurements_by_po_domain.items():
            procurements_list, rules = zip(*procurements_rules)
            origins = set(p.origin for p in procurements_list if p.origin)
            company_id = rules[0].company_id or procurements_list[0].company_id

            for procurement in procurements_list:
                if procurement.product_uom.compare(procurement.product_qty, 0.0) < 0:
                    continue

                positive_values = [p.values for p in procurements_list
                                   if procurement.product_uom.compare(p.product_qty, 0.0) >= 0]
                if not positive_values:
                    continue

                # Toujours créer un nouveau PO (comportement block)
                vals = rules[0]._prepare_purchase_order(company_id, origins, positive_values)
                vals['block_auto_purchase_order'] = True
                po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)

                po_lines_by_product = {}
                grouped_po_lines = odoo_groupby(
                    po.order_line.filtered(lambda l: not l.display_type),
                    key=lambda l: l.product_id.id,
                )
                for product_id, po_lines in grouped_po_lines:
                    po_lines_by_product[product_id] = self.env['purchase.order.line'].concat(*po_lines)

                po_line_values = []
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if not po_line:
                    po_line_values.append(
                        self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                            *procurement, po
                        )
                    )
                    order_date_planned = procurement.values['date_planned'] - relativedelta(
                        days=procurement.values['supplier'].delay)
                    if fields.Date.to_date(order_date_planned) < fields.Date.to_date(po.date_order):
                        po.date_order = order_date_planned

                self.env['purchase.order.line'].sudo().create(po_line_values)

    def unique_po_purchaceorder(self, procurements):
        """Garantit un seul PO par origine/commande de vente."""
        procurements_by_po_domain = defaultdict(list)
        errors = []

        for procurement, rule in procurements:
            company_id = rule.company_id or procurement.company_id

            supplier = rule._get_matching_supplier(
                procurement.product_id, procurement.product_qty, procurement.product_uom,
                company_id, procurement.values,
            )

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s '
                    '(no vendor defined, minimum quantity not reached, dates not valid, ...). '
                    'Go on the product form and complete the list of vendors.',
                    procurement.product_id.display_name,
                )
                errors.append((procurement, msg))
                continue

            procurement.values['supplier'] = supplier
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(company_id, procurement.values, supplier.partner_id)
            procurements_by_po_domain[domain].append((procurement, rule))

        if errors:
            raise ProcurementException(errors)

        for domain, procurements_rules in procurements_by_po_domain.items():
            procurements_list, rules = zip(*procurements_rules)
            origins = set(p.origin for p in procurements_list if p.origin)
            company_id = rules[0].company_id or procurements_list[0].company_id

            # Recherche un PO existant par origine (1 PO par SO)
            domain_with_origin = domain + (('origin', '=', str(origins).replace('{', '').replace('}', '')),)
            po = self.env['purchase.order'].sudo().search([dom for dom in domain_with_origin], limit=1)

            if not po:
                positive_values = [p.values for p in procurements_list
                                   if p.product_uom.compare(p.product_qty, 0.0) >= 0]
                if positive_values:
                    vals = rules[0]._prepare_purchase_order(company_id, origins, positive_values)
                    vals['unique_purchase_order'] = True
                    po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)
            else:
                reference_ids = set()
                for procurement in procurements_list:
                    reference_ids |= set(procurement.values.get('reference_ids', self.env['stock.reference']).ids)
                po.reference_ids = [Command.link(ref_id) for ref_id in reference_ids]
                # Mettre à jour l'origine
                if po.origin:
                    missing_origins = origins - set(po.origin.split(', '))
                    if missing_origins:
                        po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
                else:
                    po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements_list)
            procurements_list = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = odoo_groupby(
                po.order_line.filtered(lambda l: not l.display_type),
                key=lambda l: l.product_id.id,
            )
            for product_id, po_lines in grouped_po_lines:
                po_lines_by_product[product_id] = self.env['purchase.order.line'].concat(*po_lines)

            po_line_values = []
            for procurement in procurements_list:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    vals = self._update_purchase_order_line(
                        procurement.product_id, procurement.product_qty, procurement.product_uom,
                        company_id, procurement.values, po_line,
                    )
                    po_line.sudo().write(vals)
                else:
                    if procurement.product_uom.compare(procurement.product_qty, 0) <= 0:
                        continue
                    po_line_values.append(
                        self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                            *procurement, po
                        )
                    )
                    order_date_planned = procurement.values['date_planned'] - relativedelta(
                        days=procurement.values['supplier'].delay)
                    if fields.Date.to_date(order_date_planned) < fields.Date.to_date(po.date_order):
                        po.date_order = order_date_planned

            self.env['purchase.order.line'].sudo().create(po_line_values)

    @api.model
    def _run_buy(self, procurements):
        vals = {}

        for procurement, rule in procurements:
            company_id = rule.company_id or procurement.company_id

            supplier = rule._get_matching_supplier(
                procurement.product_id, procurement.product_qty, procurement.product_uom,
                company_id, procurement.values,
            )

            if not supplier:
                # Pas de fournisseur : laisser le natif gérer (cancel/notify)
                super(StockRule, self)._run_buy([(procurement, rule)])
                continue

            partner = supplier.partner_id
            procurement.values['supplier'] = supplier
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            # En v19, group_id n'existe plus — on retrouve la SO via sale_line_id dans values
            sale_line_id = procurement.values.get('sale_line_id')
            sale_order = self.env['sale.order.line'].browse(sale_line_id).order_id if sale_line_id else False
            new_sale_order = not bool(sale_order.purchase_order_count) if sale_order else True

            if partner.id in vals:
                vals[partner.id]['new_sale_order'] = new_sale_order
                vals[partner.id]['sale_order_id'] = sale_order
                vals[partner.id]['values'].append((procurement, rule))
            else:
                vals[partner.id] = {
                    'block_auto_purchase_order': partner.block_auto_purchase_order,
                    'unique_purchase_order': partner.unique_purchase_order,
                    'new_sale_order': new_sale_order,
                    'sale_order_id': sale_order,
                    'values': [(procurement, rule)],
                }

        for val_key, val_data in vals.items():
            partner_id = self.env['res.partner'].browse(val_key)

            if partner_id.block_auto_purchase_order:
                if val_data['new_sale_order']:
                    self.block_po_purchaceorder(val_data['values'])
            elif partner_id.unique_purchase_order:
                if val_data['new_sale_order']:
                    self.unique_po_purchaceorder(val_data['values'])
            else:
                super(StockRule, self)._run_buy(val_data['values'])
