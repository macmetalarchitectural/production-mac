# -*- coding: utf-8 -*-
from odoo import models, api

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


class E3KProjectTask(models.Model):
    _inherit = "project.task"

    def _auto_subscribe_followers(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        creator_follow = str2bool(IrConfigParameter.get_param('task_creator_follow'))
        assignee_follow = str2bool(IrConfigParameter.get_param('task_assignee_follow'))
        customer_follow = str2bool(IrConfigParameter.get_param('task_customer_follow'))

        creator_notify = str2bool(IrConfigParameter.get_param('task_creator_notify'))
        assignee_notify = str2bool(IrConfigParameter.get_param('task_assignee_notify'))
        customer_notify = str2bool(IrConfigParameter.get_param('task_customer_notify'))
        partners_to_notify = []

        for task in self:
            followers = task.message_follower_ids.mapped('partner_id')
            follower_to_remove = []
            task_assignees = task.mapped('user_ids.partner_id')
            task_creator = task.create_uid.partner_id
            task_customer = task.partner_id or task.project_id.partner_id

            if creator_follow:
                if task_creator and task_creator not in followers:
                    task.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(task_creator.ids)
                    if creator_notify:
                        partners_to_notify.append(task_creator.id)
            elif task_creator in followers:
                follower_to_remove.append(task_creator)

            if assignee_follow:
                for task_assignee in task_assignees:
                    if task_assignee and task_assignee not in followers:
                        task.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(task_assignee.ids)
                        if assignee_notify:
                            partners_to_notify.append(task_assignee.id)
            else:
                for task_assignee in task_assignees:
                    if task_assignee in followers:
                        follower_to_remove.append(task_assignee)

            if customer_follow:
                if task_customer and task_customer not in followers:
                    task.with_context(mail_auto_subscribe_no_notify=True).message_subscribe(task_customer.ids)
                    if customer_notify:
                        partners_to_notify.append(task_customer.id)
            else:
                if task_customer in followers:
                    follower_to_remove.append(task_customer)
                for child in task_customer.child_ids:
                    if child in followers:
                        follower_to_remove.append(task_customer)
                        follower_to_remove.append(child)

            task.message_follower_ids.filtered(lambda f: f.partner_id in follower_to_remove).sudo().unlink()
        self._e3k_notify_partners(partners_to_notify)

    @api.model
    def create(self, values):
        task = super(E3KProjectTask, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)
        ).create(values)
        task.message_follower_ids.unlink()
        task._auto_subscribe_followers()
        return task

    def write(self, values):
        res = super(E3KProjectTask, self.with_context(
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True)
        ).write(values)
        if 'partner_id' in values or 'user_id' in values:
            self._auto_subscribe_followers()
        return res
