# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import datetime
from odoo.tests import common


class TestStockMoveOriginCustomer(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.customer = cls.env['res.partner'].create({'name': 'tcustomer'})
        cls.partner = cls.env['res.partner'].create({'name': 'tpartner'})
        cls.product = cls.env['product.product'].search([])[0]
        so_name = 'SO01'
        cls.sale_order = cls.env['sale.order'].create({
            'name': so_name,
            'partner_id': cls.customer.id
        })

        cls.purchase_order = cls.env['purchase.order'].create({
            'name': 'PO01',
            'partner_id': cls.partner.id
        })

        # for odd reasons, if I set the origin of the PO at the create step,
        # origin stays at False.
        cls.purchase_order.origin = cls.sale_order.name

        cls.purchase_order_line = cls.env['purchase.order.line'].create({
            'name': 'tpurchaseline',
            'product_qty': 1.0,
            'date_planned': datetime.datetime.today(),
            'product_uom': cls.product.uom_id.id,
            'price_unit': 1.0,
            'order_id': cls.purchase_order.id,
            'product_id': cls.product.id,
        })
        cls.stock_location = cls.env['stock.location'].create({'name': 'tstocklocation'})
        cls.stock_location_dest = cls.env['stock.location'].create({'name': 'tstocklocation'})
        cls.stock_picking = cls.env['stock.picking'].create({
            'name': 'picking01',
            'purchase_id': cls.purchase_order.id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.stock_location_dest.id,
            'picking_type_id': cls.env['stock.picking.type'].search([])[0].id,
        })

        cls.stock_move = cls.env['stock.move'].create({
            'name': 'move01',
            'picking_id': cls.stock_picking.id,
            'product_id': cls.product.id,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.stock_location_dest.id,
            'purchase_line_id': cls.purchase_order_line.id,
        })

    def test_originCustomerValue(self):
        """ The value of the field origin customer has to be the same as the customer that is related to the
        sale order.

        See TA#7272
        """
        assert self.stock_move.origin_customer_id == self.customer
