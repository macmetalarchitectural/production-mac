# -*- coding: utf-8 -*-
from odoo import models, api, fields

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KStockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, values):
        picking = super(E3KStockPicking, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)).create(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        
        picking_creator_follow = IrConfigParameter.get_param('picking_creator_follow')
        picking_salerep_follow = IrConfigParameter.get_param('picking_salerep_follow')
        picking_customer_follow = IrConfigParameter.get_param('picking_customer_follow')

        picking_creator_notify = str2bool(IrConfigParameter.get_param('picking_creator_notify'))
        picking_salerep_notify = str2bool(IrConfigParameter.get_param('picking_salerep_notify'))
        picking_customer_notify = str2bool(IrConfigParameter.get_param('picking_customer_notify'))

        if picking.message_follower_ids:
            for follower in picking.message_follower_ids:

                follower_to_remove_ids = self.env['mail.followers']

                if picking.create_uid.partner_id.id == follower.partner_id.id and not picking_creator_follow:
                    follower_to_remove_ids = follower

                if picking.partner_id.id == follower.partner_id.id and not picking_customer_follow:
                    follower_to_remove_ids = follower

                if picking.user_id.partner_id.id == follower.partner_id.id and not picking_salerep_follow:
                    follower_to_remove_ids = follower

                if follower_to_remove_ids:
                    follower_to_remove_ids.sudo().unlink()

        return picking

    def write(self, values):
        picking = super(E3KStockPicking, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)).write(values)
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        picking_salerep_follow = IrConfigParameter.get_param('picking_salerep_follow')
        picking_customer_follow = IrConfigParameter.get_param('picking_customer_follow')

        picking_salerep_notify = str2bool(IrConfigParameter.get_param('picking_salerep_notify'))
        picking_customer_notify = str2bool(IrConfigParameter.get_param('picking_customer_notify'))

        for rec in self:
            for follower in rec.message_follower_ids:

                follower_to_remove_ids = self.env['mail.followers']

                if rec.partner_id.id == follower.partner_id.id and not picking_customer_follow:
                    follower_to_remove_ids = follower

                if rec.user_id.partner_id.id == follower.partner_id.id and not picking_salerep_follow:
                    follower_to_remove_ids = follower

                if follower_to_remove_ids:
                    follower_to_remove_ids.sudo().unlink()

        return picking


