from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        if 'property_purchase_currency_id' in vals:
            currency_id = self.env['res.currency'].search([('id', '=', vals['property_purchase_currency_id'])])

            old_tag_id = self.env['res.partner.category'].search([('name', '=', self.property_purchase_currency_id.name)])
            tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.name)])

            if not tag_id:
                raise UserError('La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact'%currency_id.name)
            else:
                vals.update({"category_id": [[3, old_tag_id[0].id] if old_tag_id else False , [4, tag_id[0].id]]})

        result = super(ResPartner, self).write(vals)

        return result