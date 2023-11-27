# -*- coding: utf-8 -*-
from odoo import http

# class FleetCapacity(http.Controller):
#     @http.route('/fleet_capacity/fleet_capacity/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_capacity/fleet_capacity/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_capacity.listing', {
#             'root': '/fleet_capacity/fleet_capacity',
#             'objects': http.request.env['fleet_capacity.fleet_capacity'].search([]),
#         })

#     @http.route('/fleet_capacity/fleet_capacity/objects/<model("fleet_capacity.fleet_capacity"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_capacity.object', {
#             'object': obj
#         })