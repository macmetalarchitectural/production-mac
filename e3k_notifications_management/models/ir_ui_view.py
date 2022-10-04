from odoo import api, models, SUPERUSER_ID


class E3KIrUiView(models.AbstractModel):
    _inherit = 'ir.ui.view'

    def _render(self, values=None, engine='ir.qweb', minimal_qcontext=False):
        e3k_user_name = self.env.context.get('e3k_user_name')
        e3k_message_user_assigned = self.env.ref('e3k_notifications_management.message_user_assigned', False)
        if e3k_user_name and e3k_message_user_assigned and self == e3k_message_user_assigned:
            if not isinstance(values, dict):
                values = {
                    'e3k_user_name': e3k_user_name
                }
            else:
                values.update({
                    'e3k_user_name': e3k_user_name
                })
        return super(E3KIrUiView, self)._render(values, engine, minimal_qcontext)

    @api.model
    def _prepare_qcontext(self):
        qcontext = super(E3KIrUiView, self)._prepare_qcontext()
        e3k_user_name = self.env.context.get('e3k_user_name')
        if e3k_user_name:
            qcontext.update({
                'e3k_user_name': e3k_user_name
            })
        return qcontext
