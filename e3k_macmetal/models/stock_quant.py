# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.tools import float_is_zero

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    note = fields.Char('Note')  # no-check
    e3k_lot_ref = fields.Char(related='lot_id.ref', string='Internal Reference', store=True)

    @api.model
    def _get_inventory_fields_write(self):
        """Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`."""
        field_list = super()._get_inventory_fields_write()
        field_list.append('note')
        return field_list

    def action_clear_inventory_quantity(self):
        res = super().action_clear_inventory_quantity()
        self.note = ''
        return res

    def _get_inventory_move_values(
        self, qty, location_id, location_dest_id, note, write_uid, package_id=False, package_dest_id=False
    ):
        """Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param package_id: `stock.package`
        :param package_dest_id: `stock.package`
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        self.ensure_one()
        if float_is_zero(qty, precision_rounding=self.product_uom_id.rounding):
            name = _('Product Quantity Confirmed')
        else:
            name = _('Product Quantity Updated')

        res = {
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'restrict_partner_id': self.owner_id.id,
            'is_inventory': True,
            'picked': True,
            'move_line_ids': [
                (
                    0,
                    0,
                    {
                        'product_id': self.product_id.id,
                        'product_uom_id': self.product_uom_id.id,
                        'quantity': qty,
                        'location_id': location_id.id,
                        'location_dest_id': location_dest_id.id,
                        'company_id': self.company_id.id or self.env.company.id,
                        'lot_id': self.lot_id.id,
                        'package_id': package_id.id if package_id else False,
                        'result_package_id': package_dest_id.id if package_dest_id else False,
                        'owner_id': self.owner_id.id,
                        'note': note,
                        'write_uid': write_uid,
                    },
                )
            ],
        }
        if self.env.context.get('inventory_name'):
            res['inventory_name'] = self.env.context.get('inventory_name')
        else:
            res['inventory_name'] = name

        return res

    def _apply_inventory(self, date=None):
        # Consider the inventory_quantity as set => recompute the inventory_diff_quantity if needed
        self.inventory_quantity_set = True
        move_vals = []
        for quant in self:
            # if inventory applied from product's inverse_qty and the inventory_diff_quantity is 0,
            # we skip creating a move with 0 quantity.
            if (
                quant.env.context.get('from_inverse_qty')
                and quant.product_uom_id.compare(quant.inventory_diff_quantity, 0) == 0
            ):
                continue
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if quant.product_uom_id.compare(quant.inventory_diff_quantity, 0) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(
                        quant.inventory_diff_quantity,
                        quant.product_id.with_company(quant.company_id).property_stock_inventory,
                        quant.location_id,
                        quant.note,
                        quant.write_uid,
                        package_dest_id=quant.package_id,
                    ),
                )
            else:
                move_vals.append(
                    quant._get_inventory_move_values(
                        -quant.inventory_diff_quantity,
                        quant.location_id,
                        quant.product_id.with_company(quant.company_id).property_stock_inventory,
                        quant.note,
                        quant.write_uid,
                        package_id=quant.package_id,
                    )
                )
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves.with_context(ignore_dest_packages=True)._action_done()
        if date:
            moves.date = date
        moves._trigger_assign()
        self.location_id.sudo().write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        self.action_clear_inventory_quantity()

    @api.model
    def action_view_inventory(self):
        action = super().action_view_inventory()
        action['context']['search_default_displayable_loc'] = True
        return action
