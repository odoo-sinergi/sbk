# -*- coding: utf-8 -*-
from odoo import http

# class CrmSaleInventoryInvoiceRestApi(http.Controller):
#     @http.route('/crm_sale_inventory_invoice_rest_api/crm_sale_inventory_invoice_rest_api/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_sale_inventory_invoice_rest_api/crm_sale_inventory_invoice_rest_api/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_sale_inventory_invoice_rest_api.listing', {
#             'root': '/crm_sale_inventory_invoice_rest_api/crm_sale_inventory_invoice_rest_api',
#             'objects': http.request.env['crm_sale_inventory_invoice_rest_api.crm_sale_inventory_invoice_rest_api'].search([]),
#         })

#     @http.route('/crm_sale_inventory_invoice_rest_api/crm_sale_inventory_invoice_rest_api/objects/<model("crm_sale_inventory_invoice_rest_api.crm_sale_inventory_invoice_rest_api"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_sale_inventory_invoice_rest_api.object', {
#             'object': obj
#         })