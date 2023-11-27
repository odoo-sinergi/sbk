# -*- coding: utf-8 -*-
from odoo import http

# class GenerateLotNumProductIndate(http.Controller):
#     @http.route('/generate_lot_num_product_indate/generate_lot_num_product_indate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/generate_lot_num_product_indate/generate_lot_num_product_indate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('generate_lot_num_product_indate.listing', {
#             'root': '/generate_lot_num_product_indate/generate_lot_num_product_indate',
#             'objects': http.request.env['generate_lot_num_product_indate.generate_lot_num_product_indate'].search([]),
#         })

#     @http.route('/generate_lot_num_product_indate/generate_lot_num_product_indate/objects/<model("generate_lot_num_product_indate.generate_lot_num_product_indate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('generate_lot_num_product_indate.object', {
#             'object': obj
#         })