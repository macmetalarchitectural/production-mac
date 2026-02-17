from odoo import fields, models


class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    show_ref_on_check = fields.Boolean()  # no-check

    def _create_payment_vals_from_wizard(self, batch_results):
        payment_vals = super()._create_payment_vals_from_wizard(batch_results)
        payment_vals['show_ref_on_check'] = self.show_ref_on_check
        return payment_vals
