import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)

OPEN_DELIVERY_STATES = ('waiting', 'assigned', 'confirmed')
ST_HUBERT_DELIVERY_PICKING_TYPE_ID = 1


def migrate(cr, version):
    """Recompute e3k_sales_value on open St-Hubert delivery pickings.

    Existing records kept 0$ after the Studio-to-code migration because Odoo did
    not flag them for recomputation. New sales orders compute correctly on
    confirmation; this script backfills open deliveries still in progress.
    """
    env = util.env(cr)
    pickings = env['stock.picking'].search([
        ('picking_type_id', '=', ST_HUBERT_DELIVERY_PICKING_TYPE_ID),
        ('state', 'in', OPEN_DELIVERY_STATES),
    ])
    pickings._compute_e3k_sales_value()
    pickings.flush_recordset(['e3k_sales_value'])
    _logger.info(
        "Recomputed e3k_sales_value for %s open St-Hubert delivery pickings",
        len(pickings),
    )
