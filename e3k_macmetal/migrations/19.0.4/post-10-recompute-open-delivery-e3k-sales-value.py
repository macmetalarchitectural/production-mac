import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)

BATCH_SIZE = 200
OPEN_DELIVERY_STATES = ('waiting', 'assigned', 'confirmed')
ST_HUBERT_DELIVERY_PICKING_TYPE_ID = 1


def _recompute_e3k_sales_value_in_batches(env, domain):
    Picking = env['stock.picking']
    total = 0
    last_id = 0
    while True:
        pickings = Picking.search(
            domain + [('id', '>', last_id)],
            limit=BATCH_SIZE,
            order='id',
        )
        if not pickings:
            break
        pickings._compute_e3k_sales_value()
        pickings.flush_recordset(['e3k_sales_value'])
        env.invalidate_all()
        total += len(pickings)
        last_id = pickings[-1].id
        _logger.info(
            "Recomputed e3k_sales_value for %s open delivery pickings so far (last id: %s)",
            total,
            last_id,
        )
    return total


def migrate(cr, version):
    """Recompute e3k_sales_value on open St-Hubert delivery pickings.

    Existing records kept 0$ after the Studio-to-code migration because Odoo did
    not flag them for recomputation. New sales orders compute correctly on
    confirmation; this script backfills open deliveries still in progress.
    """
    env = util.env(cr)
    domain = [
        ('picking_type_id', '=', ST_HUBERT_DELIVERY_PICKING_TYPE_ID),
        ('state', 'in', OPEN_DELIVERY_STATES),
    ]
    total = _recompute_e3k_sales_value_in_batches(env, domain)
    _logger.info(
        "Recomputed e3k_sales_value for %s open St-Hubert delivery pickings",
        total,
    )
