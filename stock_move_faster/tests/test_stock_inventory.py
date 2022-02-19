# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestStockInventory(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'Category 1',
        })
        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': cls.category.id,
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'Product B',
            'type': 'product',
            'categ_id': cls.category.id,
        })

        cls.warehouse = cls.env.ref('stock.warehouse0')

        cls.env['stock.quant'].create({
            'product_id': cls.product_a.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 10,
        })

        cls.env['stock.quant'].create({
            'product_id': cls.product_b.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 20,
        })

    def test_whenRunningInventory_thenProductsAreProperlyMoved(self):
        assert self.product_a.qty_available == 10
        assert self.product_b.qty_available == 20

        self._run_inventory()

        assert self.product_a.qty_available == 15
        assert self.product_b.qty_available == 25

    def _run_inventory(self):
        """Run an inventory with 15 x Product A and 25 x Product B."""
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'category_id': self.category.id,
        })
        inventory.action_start()
        line_a = inventory.line_ids.filtered(lambda l: l.product_id == self.product_a)
        line_b = inventory.line_ids.filtered(lambda l: l.product_id == self.product_b)
        line_a.product_qty = 15
        line_b.product_qty = 25
        inventory.action_done()

    def test_whenRunningStockPicking_thenProductsAreProperlyMoved(self):
        assert self.product_a.qty_available == 10
        assert self.product_b.qty_available == 20

        self._run_stock_picking()

        assert self.product_a.qty_available == 15
        assert self.product_b.qty_available == 30

    def test_whenRunningStockPicking_thenOnlyOneBackorderIsCreated(self):
        picking = self._run_stock_picking()

        backorder = self.env['stock.picking'].search([('backorder_id', '=', picking.id)])
        assert len(backorder) == 1
        assert len(backorder.move_lines) == 2

        backorder_of_backorder = self.env['stock.picking'].search(
            [('backorder_id', '=', backorder.id)])
        assert not backorder_of_backorder

    def _run_stock_picking(self):
        """Run a reception picking with 5 x Product A and 10 x Product B."""
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.warehouse.in_type_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.warehouse.lot_stock_id.id,
            'move_lines': [
                (0, 0, {
                    'name': '/',
                    'product_id': self.product_a.id,
                    'product_uom_qty': 100,
                    'product_uom': self.product_a.uom_id.id,
                }),
                (0, 0, {
                    'name': '/',
                    'product_id': self.product_b.id,
                    'product_uom_qty': 200,
                    'product_uom': self.product_b.uom_id.id,
                }),
            ],
        })
        picking.action_assign()

        line_a = picking.move_line_ids.filtered(lambda l: l.product_id == self.product_a)
        line_b = picking.move_line_ids.filtered(lambda l: l.product_id == self.product_b)
        line_a.qty_done = 5
        line_b.qty_done = 10

        picking.action_done()

        return picking
