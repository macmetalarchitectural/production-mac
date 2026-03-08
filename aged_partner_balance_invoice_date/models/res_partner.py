from odoo import fields, models, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals_category = []
            pricelist_id = vals.get('property_product_pricelist') or vals.get('specific_property_product_pricelist')
            if pricelist_id:
                currency_id = self.env['product.pricelist'].browse(pricelist_id)
                tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])
                if not tag_id:
                    raise UserError(
                        'La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact' % currency_id.currency_id.name)
                vals_category.append([4, tag_id[0].id])
                vals.update({"category_id": vals_category})

        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        for record in self:
            vals_category = []
            pricelist_id = vals.get('property_product_pricelist') or vals.get('specific_property_product_pricelist')
            if pricelist_id:
                currency_id = self.env['product.pricelist'].browse(pricelist_id)

                old_tag_id = self.env['res.partner.category'].search(
                    [('name', '=', record.property_product_pricelist.currency_id.name)])
                tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])

                if not tag_id:
                    raise UserError(
                        'La devise %s est introuvable dans les étiquettes, veuillez la configurer avant la création du contact' % currency_id.currency_id.name)
                if old_tag_id:
                    vals_category.append([3, old_tag_id[0].id])
                vals_category.append([4, tag_id[0].id])
                vals.update({"category_id": vals_category})
            elif 'property_product_pricelist' in vals or 'specific_property_product_pricelist' in vals:
                # Pricelist cleared — fall back to default company pricelist currency tag
                currency_id = self.env['product.pricelist'].search([('company_id', '=', False)], limit=1)
                tag_id = self.env['res.partner.category'].search([('name', '=', currency_id.currency_id.name)])
                if tag_id:
                    vals_category.append([4, tag_id[0].id])
                    vals.update({"category_id": vals_category})

        return super(ResPartner, self).write(vals)