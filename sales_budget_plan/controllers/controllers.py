# -*- coding: utf-8 -*-
from odoo import http

# class SalesBugetPlan(http.Controller):
#     @http.route('/sales_budget_plan/sales_budget_plan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_budget_plan/sales_budget_plan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_budget_plan.listing', {
#             'root': '/sales_budget_plan/sales_budget_plan',
#             'objects': http.request.env['sales_budget_plan.sales_budget_plan'].search([]),
#         })

#     @http.route('/sales_budget_plan/sales_budget_plan/objects/<model("sales_budget_plan.sales_budget_plan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_budget_plan.object', {
#             'object': obj
#         })
