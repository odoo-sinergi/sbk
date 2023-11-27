# -*- coding: utf-8 -*-
from odoo import http

# class ChangePaperFormatViipc(http.Controller):
#     @http.route('/change_paper_format_viipc/change_paper_format_viipc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/change_paper_format_viipc/change_paper_format_viipc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('change_paper_format_viipc.listing', {
#             'root': '/change_paper_format_viipc/change_paper_format_viipc',
#             'objects': http.request.env['change_paper_format_viipc.change_paper_format_viipc'].search([]),
#         })

#     @http.route('/change_paper_format_viipc/change_paper_format_viipc/objects/<model("change_paper_format_viipc.change_paper_format_viipc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('change_paper_format_viipc.object', {
#             'object': obj
#         })