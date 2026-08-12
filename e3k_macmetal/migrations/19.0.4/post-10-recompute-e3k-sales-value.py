import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


BATCH_SIZE = 500


def migrate(cr, version):
    """Force recompute of e3k_sales_value.

    The field used to be the stored Studio column x_studio_sales_value (renamed
    to e3k_sales_value). It is now a stored computed Monetary field. Because the
    DB column already existed, Odoo does not flag existing records for
    recomputation, so we trigger it explicitly here.

    Processed in batches to avoid hitting Odoo.sh memory limits.
    """
    cr.execute("SELECT id FROM stock_picking ORDER BY id")
    ids = [row[0] for row in cr.fetchall()]
    env = util.env(cr)
    total = len(ids)
    for start in range(0, total, BATCH_SIZE):
        batch_ids = ids[start:start + BATCH_SIZE]
        pickings = env['stock.picking'].browse(batch_ids)
        pickings._compute_e3k_sales_value()
        pickings.flush_recordset(['e3k_sales_value'])
        env.cr.commit()
        _logger.info(
            "Recomputed e3k_sales_value: %s/%s stock pickings",
            min(start + BATCH_SIZE, total), total,
        )
