# -*- coding: utf-8 -*-
from odoo import http

# class NavigationInvoicesSales(http.Controller):
#     @http.route('/navigation_invoices_sales/navigation_invoices_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/navigation_invoices_sales/navigation_invoices_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('navigation_invoices_sales.listing', {
#             'root': '/navigation_invoices_sales/navigation_invoices_sales',
#             'objects': http.request.env['navigation_invoices_sales.navigation_invoices_sales'].search([]),
#         })

#     @http.route('/navigation_invoices_sales/navigation_invoices_sales/objects/<model("navigation_invoices_sales.navigation_invoices_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('navigation_invoices_sales.object', {
#             'object': obj
#         })