from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'property_account_receivable_id' in vals and vals['property_account_receivable_id']:
                currency_id = self.env['account.account'].search([('id', '=', vals['property_account_receivable_id'])])

                old_tag_id = self.env['res.partner.category'].search(
                    [('name', '=', self.property_account_receivable_id.currency_id.name)])
                tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])

                if not tag_id:
                    raise UserError(
                        'La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact' % currency_id.currency_id.name)
                else:
                    vals_category = []
                    if old_tag_id:
                        vals_category.append([3, old_tag_id[0].id], )
                    vals_category.append([4, tag_id[0].id])
                    vals.update({"category_id": vals_category})

        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        if 'property_account_receivable_id' in vals and vals['property_account_receivable_id']:
            currency_id = self.env['account.account'].search([('id', '=', vals['property_account_receivable_id'])])

            old_tag_id = self.env['res.partner.category'].search(
                [('name', '=', self.property_account_receivable_id.currency_id.name)])
            tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])

            if not tag_id:
                raise UserError('La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact'%currency_id.currency_id.name)
            else:
                vals_category = []
                if old_tag_id:
                    vals_category.append([3, old_tag_id[0].id],)
                vals_category.append([4, tag_id[0].id])
                vals.update({"category_id": vals_category})

        return super(ResPartner, self).write(vals)
