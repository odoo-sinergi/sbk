# -*- coding: utf-8 -*-
from odoo import http

# class LotBarcodePicking(http.Controller):
#     @http.route('/lot_barcode_picking/lot_barcode_picking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lot_barcode_picking/lot_barcode_picking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lot_barcode_picking.listing', {
#             'root': '/lot_barcode_picking/lot_barcode_picking',
#             'objects': http.request.env['lot_barcode_picking.lot_barcode_picking'].search([]),
#         })

#     @http.route('/lot_barcode_picking/lot_barcode_picking/objects/<model("lot_barcode_picking.lot_barcode_picking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lot_barcode_picking.object', {
#             'object': obj
#         })