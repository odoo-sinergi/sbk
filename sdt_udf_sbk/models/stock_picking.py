# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID



class StockPicking(models.Model):
    _inherit = "stock.picking"


    no_sj_supplier = fields.Char(string='No. Surat Jalan Supplier')


    @api.onchange('no_sj_supplier')
    def onchange_no_sj_supplier(self):
        if not self.no_sj_supplier:
            return
        purchase_order = self.env['purchase.order'].sudo().search(['|',('id','=',self.purchase_id.id),('name','=',self.origin)])
        if purchase_order:
            purchase_order.sudo().write({'no_sj_supplier':self.no_sj_supplier})