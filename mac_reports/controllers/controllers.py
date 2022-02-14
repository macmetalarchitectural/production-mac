# -*- coding: utf-8 -*-
# from odoo import http


# class MacReports(http.Controller):
#     @http.route('/mac_reports/mac_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mac_reports/mac_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mac_reports.listing', {
#             'root': '/mac_reports/mac_reports',
#             'objects': http.request.env['mac_reports.mac_reports'].search([]),
#         })

#     @http.route('/mac_reports/mac_reports/objects/<model("mac_reports.mac_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mac_reports.object', {
#             'object': obj
#         })
