# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    no_sj_supplier = fields.Char(string='No. Surat Jalan Supplier')


    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({'no_sj_supplier': self.no_sj_supplier})
        return res