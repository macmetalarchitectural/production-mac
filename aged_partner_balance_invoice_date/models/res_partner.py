from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        if 'property_purchase_currency_id' in vals:
            currency_id = self.env['res.currency'].search([('id', '=', property_purchase_currency_id)])

            tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.name)])

            if not tag_id:
                raise UserError('La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact'%currency_id.name)
            else:
                vals.update({"category_id": [[6, 0, tag_id.ids]]})

        result = super(ResPartner, self).write(vals)

        return result