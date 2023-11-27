# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseOrderInternalReference(http.Controller):
#     @http.route('/purchase_order_internal_reference/purchase_order_internal_reference/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_order_internal_reference/purchase_order_internal_reference/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_order_internal_reference.listing', {
#             'root': '/purchase_order_internal_reference/purchase_order_internal_reference',
#             'objects': http.request.env['purchase_order_internal_reference.purchase_order_internal_reference'].search([]),
#         })

#     @http.route('/purchase_order_internal_reference/purchase_order_internal_reference/objects/<model("purchase_order_internal_reference.purchase_order_internal_reference"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_order_internal_reference.object', {
#             'object': obj
#         })