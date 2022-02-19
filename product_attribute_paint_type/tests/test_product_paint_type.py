# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestProductPaintType(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attribute = cls.env['product.attribute'].create({
            'name': 'Color',
        })

        cls.white = cls.env['product.attribute.value'].create({
            'name': 'White',
            'attribute_id': cls.attribute.id,
            'paint_type': 'Standard Paint',
        })

        cls.black = cls.env['product.attribute.value'].create({
            'name': 'Black',
            'attribute_id': cls.attribute.id,
            'paint_type': 'Supreme Paint',
        })

        cls.product = cls.env['product.product'].create({
            'name': 'My Product',
            'type': 'product',
            'attribute_value_ids': [(4, cls.white.id)],
        })

    def test_compute_paint_type(self):
        self.assertEqual(self.product.paint_type, 'Standard Paint')

    def test_compute_paint_type_with_no_paint_type_on_attribute_value(self):
        self.white.paint_type = None
        self.assertEqual(self.product.paint_type, '')

    def test_compute_paint_type_with_no_attribute_value_on_product(self):
        self.product.write({'attribute_value_ids': [(5, 0)]})
        self.assertEqual(self.product.paint_type, '')
