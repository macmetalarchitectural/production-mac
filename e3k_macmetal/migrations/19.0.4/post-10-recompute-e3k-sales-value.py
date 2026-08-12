import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Force recompute of e3k_sales_value.

    The field used to be the stored Studio column x_studio_sales_value (renamed
    to e3k_sales_value). It is now a stored computed Monetary field. Because the
    DB column already existed, Odoo does not flag existing records for
    recomputation, so we trigger it explicitly here.
    """
    env = util.env(cr)
    pickings = env['stock.picking'].search([])
    pickings._compute_e3k_sales_value()
    pickings.flush_recordset(['e3k_sales_value'])
    _logger.info("Recomputed e3k_sales_value for %s stock pickings", len(pickings))
