# -*- coding: utf-8 -*-

from . import models
from . import controllers

def pre_init_check(cr):
  from odoo.service import common
  from odoo.exceptions import UserError

  version_info = common.exp_version()
  server_serie = version_info.get('server_serie')
  if server_serie != '19.0':
    raise UserError('Module supports Odoo series 19.0, found: ' + server_serie)
  return True