import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = util.env(cr)
    # domaine ou le champ delivery_route n' est pas vide
    domaine_so = [('x_delivery_route', '!=', False)]
    domaine_SP = [('x_delivery_pickup', '!=', False)]

    sale_order_ids = env['sale.order'].search(domaine_so)
    all_routes_ids = env['mac.route.config'].search([])

    stock_picking_ids = env['stock.picking'].search(domaine_SP)
    stock_picking_ids.write({'delivery_pickup': True})

    for sale_order in sale_order_ids:
        routes = all_routes_ids.filtered(lambda x: x.code == sale_order.x_delivery_route)
        if routes:
            sale_order.write({'delivery_route_id': routes[0].id})
            _logger.info(f"Updated sale order {sale_order.name} with delivery route {sale_order.x_delivery_route}")
        else:
            _logger.info(
                f"Sale order {sale_order.name} has delivery route "
                f"{sale_order.x_delivery_route} but no route found with this code"
            )

    vue_to_delete = [1975, 1976]
    vues_where_to_remove = [
        3286,
        3287,
        3285,
    ]
    field = ['x_delivery_route', 'x_delivery_pickup']

    for vue_id in vues_where_to_remove:
        with util.skippable_cm(), util.edit_view(cr, view_id=vue_id) as arch:
            for f in field:
                field = arch.xpath(f"//field[@name='{f}']")
                if field:
                    parent = field[0].getparent()
                    parent.remove(field[0])
                    _logger.info(f"Removed field '{f}' from view {vue_id}")
                else:
                    _logger.info(f"field '{f}' not found")

    for view in env['ir.ui.view'].browse(vue_to_delete).exists():
        view.active = False
