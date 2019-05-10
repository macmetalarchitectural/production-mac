# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models, fields, api


class ProductTemplateWidthThickness(models.Model):
    """Add the fields width and thickness."""
    _inherit = 'product.template'

    # see TA#4895
    thickness = fields.Float()
    thickness_uom_id = fields.Many2one('product.uom')
    width = fields.Float()
    width_uom_id = fields.Many2one('product.uom')


class ProductProductWidthThickness(models.Model):
    """Add the fields width and thickness."""
    _inherit = 'product.product'

    # see TA#4895
    @api.model
    def _default_thickness(self):
        return self.product_tmpl_id.thickness

    @api.model
    def _default_thickness_uom_id(self):
        return self.product_tmpl_id.thickness_uom_id

    @api.model
    def _default_width(self):
        return self.product_tmpl_id.width

    @api.model
    def _default_width_uom_id(self):
        return self.product_tmpl_id.width_uom_id

    thickness = fields.Float(default=_default_thickness)
    thickness_uom_id = fields.Many2one('product.uom', default=_default_thickness_uom_id)
    width = fields.Float(default=_default_width)
    width_uom_id = fields.Many2one('product.uom', default=_default_width_uom_id)
