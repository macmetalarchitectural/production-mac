# -*- coding: utf-8 -*-
# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models, fields


class ProductTemplateWithPaintBatchTrack(models.Model):
    """Add the field paint_batch_track"""
    _inherit = 'product.template'

    # see TA#1778
    paint_batch_track = fields.Boolean(string='Paint Batch Track', help="Tracking of paint batches")
