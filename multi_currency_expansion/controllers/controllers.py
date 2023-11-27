# -*- coding: utf-8 -*-
from odoo import http

# class MultiCurrencyExpansion(http.Controller):
#     @http.route('/multi_currency_expansion/multi_currency_expansion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_currency_expansion/multi_currency_expansion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_currency_expansion.listing', {
#             'root': '/multi_currency_expansion/multi_currency_expansion',
#             'objects': http.request.env['multi_currency_expansion.multi_currency_expansion'].search([]),
#         })

#     @http.route('/multi_currency_expansion/multi_currency_expansion/objects/<model("multi_currency_expansion.multi_currency_expansion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_currency_expansion.object', {
#             'object': obj
#         })