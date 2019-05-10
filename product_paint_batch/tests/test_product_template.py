# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestProductTemplate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env['product.template'].create({
            'name': 'Test product',
        })

    def test_fieldPaintBatch(self):
        """
        product.template as a new boolean field called "paint_batch_track"
        Default value to False
        see TA#1778
        """
        self.assertFalse(self.product.paint_batch_track)
        self.product.write({
            'paint_batch_track': True
        })
        self.assertTrue(self.product.paint_batch_track)
