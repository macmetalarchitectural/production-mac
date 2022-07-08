from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals_category = []
            if 'property_product_pricelist' in vals:
                if vals['property_product_pricelist']:
                    currency_id = self.env['product.pricelist'].search([('id', '=', vals['property_product_pricelist'])], limit=1)

                    old_tag_id = self.env['res.partner.category'].search(
                        [('name', '=', self.property_product_pricelist.currency_id.name)])
                    tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])

                    if not tag_id:
                        raise UserError(
                            'La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact' % currency_id.currency_id.name)
                    else:
                        if old_tag_id:
                            vals_category.append([3, old_tag_id[0].id], )
                        vals_category.append([4, tag_id[0].id])
                        vals.update({"category_id": vals_category})
                else:
                    currency_id = self.env['product.pricelist'].search([('company_id', '=', False)],
                                                                       limit=1)
                    tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])
                    vals_category.append([4, tag_id[0].id])
                    vals.update({"category_id": vals_category})

        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        vals_category = []
        if 'property_product_pricelist' in vals:
            if vals['property_product_pricelist']:
                currency_id = self.env['product.pricelist'].search([('id', '=', vals['property_product_pricelist'])], limit=1)

                old_tag_id = self.env['res.partner.category'].search(
                    [('name', '=', self.property_product_pricelist.currency_id.name)])
                tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])

                if not tag_id:
                    raise UserError('La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact'%currency_id.currency_id.name)
                else:
                    if old_tag_id:
                        vals_category.append([3, old_tag_id[0].id],)
                    vals_category.append([4, tag_id[0].id])
                    vals.update({"category_id": vals_category})
            else:
                currency_id = self.env['product.pricelist'].search([('company_id', '=', False)],
                                                                   limit=1)
                tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])
                vals_category.append([4, tag_id[0].id])
                vals.update({"category_id": vals_category})

        return super(ResPartner, self).write(vals)
