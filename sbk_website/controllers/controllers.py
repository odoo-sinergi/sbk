# -*- coding: utf-8 -*-
from odoo import http

# class SbkWebsite(http.Controller):
#     @http.route('/sbk_website/sbk_website/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sbk_website/sbk_website/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sbk_website.listing', {
#             'root': '/sbk_website/sbk_website',
#             'objects': http.request.env['sbk_website.sbk_website'].search([]),
#         })

#     @http.route('/sbk_website/sbk_website/objects/<model("sbk_website.sbk_website"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sbk_website.object', {
#             'object': obj
#         })