# -*- coding: utf-8 -*-
from odoo import http

# class SalePushNotification(http.Controller):
#     @http.route('/sale_push_notification/sale_push_notification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_push_notification/sale_push_notification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_push_notification.listing', {
#             'root': '/sale_push_notification/sale_push_notification',
#             'objects': http.request.env['sale_push_notification.sale_push_notification'].search([]),
#         })

#     @http.route('/sale_push_notification/sale_push_notification/objects/<model("sale_push_notification.sale_push_notification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_push_notification.object', {
#             'object': obj
#         })