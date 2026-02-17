# -*- coding: utf-8 -*-
import re

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def compute_print_default_code(self):
        icp = self.env['ir.config_parameter'].sudo()
        return icp.get_param('e3k_default_reports.add_default_code_report') or False


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)
        return None

    def _get_aggregated_product_quantities(self, **kwargs):
        """Returns dictionary of products and corresponding
        values of interest + hs_code

        Unfortunately because we are working with aggregated data,
        we have to loop through the
        aggregation to add more values to each datum. This extension
        adds on the hs_code value.

        returns: dictionary {same_key_as_super: {same_values_as_super, hs_code}, ...}
        """
        aggregated_move_lines = super()._get_aggregated_product_quantities(**kwargs)
        for aggregated_move_line in aggregated_move_lines:
            default_code = aggregated_move_lines[aggregated_move_line]['product'].default_code  # noqa
            product_name = aggregated_move_lines[aggregated_move_line]['product'].name
            aggregated_move_lines[aggregated_move_line]['default_code'] = default_code
            aggregated_move_lines[aggregated_move_line]['product_name'] = product_name
        return aggregated_move_lines


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_name_no_ref(self):
        for rec in self:
            if rec.name:
                return re.sub(r'\[.*?\]', '', rec.name)

        return None
