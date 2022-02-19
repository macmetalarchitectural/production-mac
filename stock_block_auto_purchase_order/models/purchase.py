# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api
from odoo.addons.purchase.models.purchase import PurchaseOrder


class PartnerBlockAutoPO(models.Model):
    _inherit = 'res.partner'

    block_auto_purchase_order = fields.Boolean(
        string='Block Automatic Products On PO',
        default=False,
        help="This field is automatically propagated to the PO. "
        "When checked on the PO, it prevents products from being automatically added "
        "by the system."
    )


class ProcurementRuleBlockAutoMakePO(models.Model):
    """ Update the domain of make PO to consider the field block_auto_purchase_order """
    _inherit = 'procurement.rule'

    def _make_po_get_domain(self, values, partner):
        """ Take in count the field block_auto_purchase_order in the domain."""
        domain = super()._make_po_get_domain(values, partner)
        domain += (('block_auto_purchase_order', '=', False),)
        return domain

    def _prepare_purchase_order(
        self, product_id, product_qty, product_uom, origin, values, partner
    ):
        """Set block_auto_purchase_order when preparing a new purchase order."""
        res = super()._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner)
        res['block_auto_purchase_order'] = partner.block_auto_purchase_order
        return res


class PurchaseOrderBlockAutoMake(models.Model):
    _inherit = 'purchase.order'

    block_auto_purchase_order = fields.Boolean(
        string='Block Automatic Product Add',
        default=False,
        states=PurchaseOrder.READONLY_STATES,
        help="When checked, this field prevents products from being automatically added "
        "to the PO by the system."
    )

    @api.onchange('partner_id')
    def _block_auto_purchase_order(self):
        self.block_auto_purchase_order = self.partner_id.block_auto_purchase_order
