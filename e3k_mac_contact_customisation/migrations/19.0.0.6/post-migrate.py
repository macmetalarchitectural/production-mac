import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Migration %s: starting", version)
    _logger.info("Migration %s: done", version)
