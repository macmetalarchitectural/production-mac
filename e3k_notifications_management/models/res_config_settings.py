# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class E3KResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Followers
    quo_creator_follow = fields.Boolean("Quotation Followed By the Creator ")
    quo_salerep_follow = fields.Boolean("Quotation Followed By the Sale Representative ")
    quo_customer_follow = fields.Boolean("Quotation Followed By the Customer ")

    so_creator_follow = fields.Boolean("Sale Order Followed By the Creator ")
    so_seller_follow = fields.Boolean("Sale Order Followed By the Seller ")
    so_customer_follow = fields.Boolean("Sale Order Followed By the Customer ")

    inv_creator_follow = fields.Boolean("Invoice Followed By the Creator ")
    inv_seller_follow = fields.Boolean("Invoice Followed By the Seller ")
    inv_customer_follow = fields.Boolean("Invoice Followed By the Customer ")

    req_quo_creator_follow = fields.Boolean("Request For Quotation Followed By the Creator ")
    req_quo_purrep_follow = fields.Boolean("Request For Quotation Followed By Purchase Representative ")
    req_quo_vendor_follow = fields.Boolean("Request For Quotation Followed By the Vendor ")

    po_creator_follow = fields.Boolean("Purchase Order Followed By the Creator ")
    po_purrep_follow = fields.Boolean("Purchase Order Followed By Purchase Representative ")
    po_vendor_follow = fields.Boolean("Purchase Order Followed By the Vendor ")

    bill_creator_follow = fields.Boolean("Bill Followed By the Creator ")
    bill_purrep_follow = fields.Boolean("Bill Followed By the Purchase Representative ")
    bill_vendor_follow = fields.Boolean("Bill Followed By the Vendor ")

    cont_creator_follow = fields.Boolean("Contact Followed By the Creator ")
    cont_salerep_follow = fields.Boolean("Contact Followed By the Sale Representative ")
    cont_customer_follow = fields.Boolean("Contact Followed By the Customer ")

    picking_creator_follow = fields.Boolean("Transfer Followed By the Creator ")
    picking_salerep_follow = fields.Boolean("Transfer Followed By the Sale Representative ")
    picking_customer_follow = fields.Boolean("Transfer Followed By the Customer ")

    entry_creator_follow = fields.Boolean("Entry Followed By the Creator ")
    entry_salerep_follow = fields.Boolean("Entry Followed By the Seller ")
    entry_customer_follow = fields.Boolean("Entry Followed By the Customer ")

    task_creator_follow = fields.Boolean("Task Followed By the Creator")
    task_assignee_follow = fields.Boolean("Task Followed By the Assignees")
    task_customer_follow = fields.Boolean("Task Followed By the Customer")

    # Notifications
    quo_creator_notify = fields.Boolean("Notify creator of Quotation assignation")
    quo_salerep_notify = fields.Boolean("Notify Sale Representative of Quotation assignation")
    quo_customer_notify = fields.Boolean("Notify Customer of Quotation assignation")

    so_creator_notify = fields.Boolean("Notify creator of Sale Order assignation")
    so_seller_notify = fields.Boolean("Notify seller of Sale Order assignation")
    so_customer_notify = fields.Boolean("Notify customer of Sale Order assignation")
    so_vendor_notify = fields.Boolean("Notify vendor of Sale Order assignation")

    inv_creator_notify = fields.Boolean("Notify creator of invoice assignation")
    inv_seller_notify = fields.Boolean("Notify seller of invoice assignation")
    inv_customer_notify = fields.Boolean("Notify customer of invoice assignation")

    req_quo_creator_notify = fields.Boolean("Notify creator of rfq assignation")
    req_quo_purrep_notify = fields.Boolean("Notify purchase responsive of rfq assignation")
    req_quo_vendor_notify = fields.Boolean("Notify vendor of rfq assignation ")

    po_creator_notify = fields.Boolean("Notify creator of PO assignation")
    po_purrep_notify = fields.Boolean("Notify purchase responsive of PO assignation")
    po_vendor_notify = fields.Boolean("Notify vendor of PO assignation")

    bill_creator_notify = fields.Boolean("Notify creator of bill assignation")
    bill_purrep_notify = fields.Boolean("Notify purchase responsive of bill assignation")
    bill_vendor_notify = fields.Boolean("Notify vendor of bill assignation")

    cont_creator_notify = fields.Boolean("Notify creator of Contact assignation")
    cont_salerep_notify = fields.Boolean("Notify sale responsive of Contact assignation")
    cont_customer_notify = fields.Boolean("Notify customer of Contact assignation")

    picking_creator_notify = fields.Boolean("Notify creator of stock picking assignation")
    picking_salerep_notify = fields.Boolean("Notify sale responsive of stock picking assignation")
    picking_customer_notify = fields.Boolean("Notify customer of stock picking assignation")

    entry_creator_notify = fields.Boolean("Notify creator of entry assignation")
    entry_salerep_notify = fields.Boolean("Notify sale responsive of entry assignation")
    entry_customer_notify = fields.Boolean("Notify customer of entry assignation")

    task_creator_notify = fields.Boolean("Notify creator of task assignation")
    task_assignee_notify = fields.Boolean("Notify assignees of task assignation")
    task_customer_notify = fields.Boolean("Notify customer of task assignation")

    @api.model
    def get_values(self):
        res = super(E3KResConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        # Followers
        res['quo_creator_follow'] = IrConfigParameter.get_param('quo_creator_follow')
        res['quo_salerep_follow'] = IrConfigParameter.get_param('quo_salerep_follow')
        res['quo_customer_follow'] = IrConfigParameter.get_param('quo_customer_follow')

        res['so_creator_follow'] = IrConfigParameter.get_param('so_creator_follow')
        res['so_seller_follow'] = IrConfigParameter.get_param('so_seller_follow')
        res['so_customer_follow'] = IrConfigParameter.get_param('so_customer_follow')

        res['inv_creator_follow'] = IrConfigParameter.get_param('inv_creator_follow')
        res['inv_seller_follow'] = IrConfigParameter.get_param('inv_seller_follow')
        res['inv_customer_follow'] = IrConfigParameter.get_param('inv_customer_follow')

        res['req_quo_creator_follow'] = IrConfigParameter.get_param('req_quo_creator_follow')
        res['req_quo_purrep_follow'] = IrConfigParameter.get_param('req_quo_purrep_follow')
        res['req_quo_vendor_follow'] = IrConfigParameter.get_param('req_quo_vendor_follow')

        res['po_creator_follow'] = IrConfigParameter.get_param('po_creator_follow')
        res['po_purrep_follow'] = IrConfigParameter.get_param('po_purrep_follow')
        res['po_vendor_follow'] = IrConfigParameter.get_param('po_vendor_follow')

        res['bill_creator_follow'] = IrConfigParameter.get_param('bill_creator_follow')
        res['bill_purrep_follow'] = IrConfigParameter.get_param('bill_purrep_follow')
        res['bill_vendor_follow'] = IrConfigParameter.get_param('bill_vendor_follow')

        res['cont_creator_follow'] = IrConfigParameter.get_param('cont_creator_follow')
        res['cont_salerep_follow'] = IrConfigParameter.get_param('cont_salerep_follow')
        res['cont_customer_follow'] = IrConfigParameter.get_param('cont_customer_follow')

        res['picking_creator_follow'] = IrConfigParameter.get_param('picking_creator_follow')
        res['picking_salerep_follow'] = IrConfigParameter.get_param('picking_salerep_follow')
        res['picking_customer_follow'] = IrConfigParameter.get_param('picking_customer_follow')

        res['entry_creator_follow'] = IrConfigParameter.get_param('entry_creator_follow')
        res['entry_salerep_follow'] = IrConfigParameter.get_param('entry_salerep_follow')
        res['entry_customer_follow'] = IrConfigParameter.get_param('entry_customer_follow')

        res['task_creator_follow'] = IrConfigParameter.get_param('task_creator_follow')
        res['task_assignee_follow'] = IrConfigParameter.get_param('task_assignee_follow')
        res['task_customer_follow'] = IrConfigParameter.get_param('task_customer_follow')

        # Notifications
        res['quo_creator_notify'] = IrConfigParameter.get_param('quo_creator_notify')
        res['quo_salerep_notify'] = IrConfigParameter.get_param('quo_salerep_notify')
        res['quo_customer_notify'] = IrConfigParameter.get_param('quo_customer_notify')

        res['so_creator_notify'] = IrConfigParameter.get_param('so_creator_notify')
        res['so_seller_notify'] = IrConfigParameter.get_param('so_seller_notify')
        res['so_customer_notify'] = IrConfigParameter.get_param('so_customer_notify')
        res['so_vendor_notify'] = IrConfigParameter.get_param('so_vendor_notify')

        res['inv_creator_notify'] = IrConfigParameter.get_param('inv_creator_notify')
        res['inv_seller_notify'] = IrConfigParameter.get_param('inv_seller_notify')
        res['inv_customer_notify'] = IrConfigParameter.get_param('inv_customer_notify')

        res['req_quo_creator_notify'] = IrConfigParameter.get_param('req_quo_creator_notify')
        res['req_quo_purrep_notify'] = IrConfigParameter.get_param('req_quo_purrep_notify')
        res['req_quo_vendor_notify'] = IrConfigParameter.get_param('req_quo_vendor_notify')

        res['po_creator_notify'] = IrConfigParameter.get_param('po_creator_notify')
        res['po_purrep_notify'] = IrConfigParameter.get_param('po_purrep_notify')
        res['po_vendor_notify'] = IrConfigParameter.get_param('po_vendor_notify')

        res['bill_creator_notify'] = IrConfigParameter.get_param('bill_creator_notify')
        res['bill_purrep_notify'] = IrConfigParameter.get_param('bill_purrep_notify')
        res['bill_vendor_notify'] = IrConfigParameter.get_param('bill_vendor_notify')

        res['cont_creator_notify'] = IrConfigParameter.get_param('cont_creator_notify')
        res['cont_salerep_notify'] = IrConfigParameter.get_param('cont_salerep_notify')
        res['cont_customer_notify'] = IrConfigParameter.get_param('cont_customer_notify')

        res['picking_creator_notify'] = IrConfigParameter.get_param('picking_creator_notify')
        res['picking_salerep_notify'] = IrConfigParameter.get_param('picking_salerep_notify')
        res['picking_customer_notify'] = IrConfigParameter.get_param('picking_customer_notify')

        res['entry_creator_notify'] = IrConfigParameter.get_param('entry_creator_notify')
        res['entry_salerep_notify'] = IrConfigParameter.get_param('entry_salerep_notify')
        res['entry_customer_notify'] = IrConfigParameter.get_param('entry_customer_notify')

        res['task_creator_notify'] = IrConfigParameter.get_param('task_creator_notify')
        res['task_assignee_notify'] = IrConfigParameter.get_param('task_assignee_notify')
        res['task_customer_notify'] = IrConfigParameter.get_param('task_customer_notify')

        return res

    @api.model
    def set_values(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        # Followers
        IrConfigParameter.set_param('quo_creator_follow', self.quo_creator_follow)
        IrConfigParameter.set_param('quo_salerep_follow', self.quo_salerep_follow)
        IrConfigParameter.set_param('quo_customer_follow', self.quo_customer_follow)

        IrConfigParameter.set_param('so_creator_follow', self.so_creator_follow)
        IrConfigParameter.set_param('so_seller_follow', self.so_seller_follow)
        IrConfigParameter.set_param('so_customer_follow', self.so_customer_follow)

        IrConfigParameter.set_param('inv_creator_follow', self.inv_creator_follow)
        IrConfigParameter.set_param('inv_seller_follow', self.inv_seller_follow)
        IrConfigParameter.set_param('inv_customer_follow', self.inv_customer_follow)

        IrConfigParameter.set_param('req_quo_creator_follow', self.req_quo_creator_follow)
        IrConfigParameter.set_param('req_quo_purrep_follow', self.req_quo_purrep_follow)
        IrConfigParameter.set_param('req_quo_vendor_follow', self.req_quo_vendor_follow)

        IrConfigParameter.set_param('po_creator_follow', self.po_creator_follow)
        IrConfigParameter.set_param('po_purrep_follow', self.po_purrep_follow)
        IrConfigParameter.set_param('po_vendor_follow', self.po_vendor_follow)

        IrConfigParameter.set_param('bill_creator_follow', self.bill_creator_follow)
        IrConfigParameter.set_param('bill_purrep_follow', self.bill_purrep_follow)
        IrConfigParameter.set_param('bill_vendor_follow', self.bill_vendor_follow)

        IrConfigParameter.set_param('cont_creator_follow', self.cont_creator_follow)
        IrConfigParameter.set_param('cont_salerep_follow', self.cont_salerep_follow)
        IrConfigParameter.set_param('cont_customer_follow', self.cont_customer_follow)

        IrConfigParameter.set_param('picking_creator_follow', self.picking_creator_follow)
        IrConfigParameter.set_param('picking_salerep_follow', self.picking_salerep_follow)
        IrConfigParameter.set_param('picking_customer_follow', self.picking_customer_follow)

        IrConfigParameter.set_param('entry_creator_follow', self.entry_creator_follow)
        IrConfigParameter.set_param('entry_salerep_follow', self.entry_salerep_follow)
        IrConfigParameter.set_param('entry_customer_follow', self.entry_customer_follow)

        IrConfigParameter.set_param('task_creator_follow', self.task_creator_follow)
        IrConfigParameter.set_param('task_assignee_follow', self.task_assignee_follow)
        IrConfigParameter.set_param('task_customer_follow', self.task_customer_follow)

        # Notifications
        IrConfigParameter.set_param('quo_creator_notify', self.quo_creator_notify)
        IrConfigParameter.set_param('quo_salerep_notify', self.quo_salerep_notify)
        IrConfigParameter.set_param('quo_customer_notify', self.quo_customer_notify)

        IrConfigParameter.set_param('so_creator_notify', self.so_creator_notify)
        IrConfigParameter.set_param('so_seller_notify', self.so_seller_notify)
        IrConfigParameter.set_param('so_customer_notify', self.so_customer_notify)
        IrConfigParameter.set_param('so_vendor_notify', self.so_vendor_notify)

        IrConfigParameter.set_param('inv_creator_notify', self.inv_creator_notify)
        IrConfigParameter.set_param('inv_seller_notify', self.inv_seller_notify)
        IrConfigParameter.set_param('inv_customer_notify', self.inv_customer_notify)

        IrConfigParameter.set_param('req_quo_creator_notify', self.req_quo_creator_notify)
        IrConfigParameter.set_param('req_quo_purrep_notify', self.req_quo_purrep_notify)
        IrConfigParameter.set_param('req_quo_vendor_notify', self.req_quo_vendor_notify)

        IrConfigParameter.set_param('po_creator_notify', self.po_creator_notify)
        IrConfigParameter.set_param('po_purrep_notify', self.po_purrep_notify)
        IrConfigParameter.set_param('po_vendor_notify', self.po_vendor_notify)

        IrConfigParameter.set_param('bill_creator_notify', self.bill_creator_notify)
        IrConfigParameter.set_param('bill_purrep_notify', self.bill_purrep_notify)
        IrConfigParameter.set_param('bill_vendor_notify', self.bill_vendor_notify)

        IrConfigParameter.set_param('cont_creator_notify', self.cont_creator_notify)
        IrConfigParameter.set_param('cont_salerep_notify', self.cont_salerep_notify)
        IrConfigParameter.set_param('cont_customer_notify', self.cont_customer_notify)

        IrConfigParameter.set_param('picking_creator_notify', self.picking_creator_notify)
        IrConfigParameter.set_param('picking_salerep_notify', self.picking_salerep_notify)
        IrConfigParameter.set_param('picking_customer_notify', self.picking_customer_notify)

        IrConfigParameter.set_param('entry_creator_notify', self.entry_creator_notify)
        IrConfigParameter.set_param('entry_salerep_notify', self.entry_salerep_notify)
        IrConfigParameter.set_param('entry_customer_notify', self.entry_customer_notify)

        IrConfigParameter.set_param('task_creator_notify', self.task_creator_notify)
        IrConfigParameter.set_param('task_assignee_notify', self.task_assignee_notify)
        IrConfigParameter.set_param('task_customer_notify', self.task_customer_notify)

        super(E3KResConfigSettings, self).set_values()
