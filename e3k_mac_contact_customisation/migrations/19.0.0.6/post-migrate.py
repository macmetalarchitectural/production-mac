import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Migration %s: starting", version)
    # TODO: add migration logic here
    _logger.info("Migration %s: done", version)
