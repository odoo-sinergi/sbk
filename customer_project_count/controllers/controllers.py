# -*- coding: utf-8 -*-
from odoo import http

# class CustomerProjectCount(http.Controller):
#     @http.route('/customer_project_count/customer_project_count/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_project_count/customer_project_count/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_project_count.listing', {
#             'root': '/customer_project_count/customer_project_count',
#             'objects': http.request.env['customer_project_count.customer_project_count'].search([]),
#         })

#     @http.route('/customer_project_count/customer_project_count/objects/<model("customer_project_count.customer_project_count"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_project_count.object', {
#             'object': obj
#         })