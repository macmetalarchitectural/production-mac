# -*- coding: utf-8 -*-

from odoo import _
from odoo.service import common
from odoo.exceptions import UserError

from . import models
from . import controllers


def pre_init_check(cr):  # pylint: disable=unused-argument
    """Check Odoo version before module installation."""
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '19.0':
        raise UserError(_('Module supports Odoo series 19.0, found: %s') % server_serie)
    return True
