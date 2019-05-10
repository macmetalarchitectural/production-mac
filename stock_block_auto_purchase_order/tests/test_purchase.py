# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import datetime

from odoo.tests import common


class TestPartnerBlockAutoPO(common.SavepointCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'tname'
        })

    def test_whenNewPartner_thenBlockAutoPOSetToFalse(self):
        self.assertFalse(self.partner.block_auto_purchase_order)


class TestProcurementRuleBlockAutoMakePO(common.SavepointCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'tname'
        })

        cls.company = cls.env['res.partner'].create({
            'name': 'tcompany',
            'is_company': True,
        })

        cls.sequence = cls.env['ir.sequence'].create({
            'name': 'tsequence',
            'code': '1',
        })
        cls.picking_type = cls.env['stock.picking.type'].create({
            'name': 'tstockpicking',
            'sequence_id': cls.sequence.id,
            'code': 'incoming',
        })

        cls.route = cls.env['stock.location.route'].create({
            'name': 'troute',
        })

        cls.rule = cls.env['procurement.rule'].create({
            'name': 'trule',
            'action': 'move',
            'route_id': cls.route.id,
            'picking_type_id': cls.picking_type.id,
        })

    def test_domainHasBlockAutoPurchaseOrderFalse(self):
        domain = self.rule._make_po_get_domain(
            {
                'company_id': self.company,
                'picking_type_id': self.picking_type,
            },
            self.partner
        )
        self.assertIn(
            ('block_auto_purchase_order', '=', False),
            domain
        )


class TestPurchaseOrderBlockAutoMake(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'tname'
        })
        currency = cls.env['res.currency'].create({
            'name': 'tcurrency',
            'symbol': ':dog:'

        })
        cls.purchase_order = cls.env['purchase.order'].create({
            'name': 'tpurchase',
            'date_order': datetime.datetime.now(),
            'partner_id': cls.partner.id,
            'currency_id': currency.id,
        })

    def test_purchaseOrderDepends(self):
        self.assertFalse(self.purchase_order.block_auto_purchase_order)

        self.partner.block_auto_purchase_order = True

        with self.env.do_in_onchange():
            self.purchase_order._block_auto_purchase_order()

        self.assertTrue(self.purchase_order.block_auto_purchase_order)
