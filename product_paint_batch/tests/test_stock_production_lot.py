# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestStockProductionLot(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.name = "1234567"
        cls.stock_production_lot = cls.env['stock.production.lot'].create({
            'name': cls.name,
            'product_id': cls.product.id,
        })
        cls.res_config_settings = cls.env['res.config.settings']

    def test_fieldPaintBatch(self):
        """
        stock.production.lot has a new field computed char called paint_batch
        see TA#1778
        """
        self.product.write({
            'paint_batch_track': False,
        })
        self.assertFalse(self.stock_production_lot.paint_batch)
        self.product.write({
            'paint_batch_track': self.name
        })
        length = int(self.env['ir.config_parameter'].sudo().get_param('product_paint_batch.paint_batch_length'))
        self.assertEqual(self.name[:length], self.stock_production_lot.paint_batch)


