import logging
from odoo.upgrade import util
from lxml import etree

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    env = util.env(cr)
    # domaine ou le champ delivery_route n' est pas vide
    domaine = [('delivery_route', '!=', False)]
    sale_order_ids = env['sale.order'].search(domaine)
    all_routes_ids = env['mac.route.config'].search([])

    for sale_order in sale_order_ids:
        routes = all_routes_ids.filtered(lambda x: x.code == sale_order.delivery_route)
        if routes:
            sale_order.write({'delivery_route_id': routes[0].id})
            _logger.info(f"Updated sale order {sale_order.name} with delivery route {sale_order.delivery_route}")
        else:
            _logger.info(f"Sale order {sale_order.name} has delivery route {sale_order.delivery_route} but no route found with this code")


    # now delete fields delivery_route
    try:
        util.remove_field(env, 'sale.order', 'delivery_route')
        _logger.info(f"Deleted field delivery_route")
    except Exception as e:
        _logger.info(f"Failed to delete field delivery_route")
