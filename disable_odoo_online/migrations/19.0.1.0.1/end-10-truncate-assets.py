import logging

from odoo.upgrade import util

e3k_logger = logging.getLogger(__name__)
E3K_PREFIX_LOG = '----------------------> e3k log : '


def truncate_ir_asset_table(cr):
    try:
        util.parallel_execute(cr, [util.format_query(cr, "TRUNCATE TABLE ir_asset")])
        e3k_logger.warning(E3K_PREFIX_LOG + "Truncate table ir_asset successfully executed")
    except Exception as e:
        e3k_logger.warning(E3K_PREFIX_LOG + f"Failed to truncate table ir_asset: {e}")


def migrate(cr, version):
    env = util.env(cr)

    truncate_ir_asset_table(cr)