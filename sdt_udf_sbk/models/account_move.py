# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID



class AccountMove(models.Model):
    _inherit = "account.move"


    no_sj_supplier = fields.Char(string='No. Surat Jalan Supplier')
    payment_date = fields.Date(string='Payment Date', compute='_compute_payment_date', store=True)

    @api.depends('state','amount_residual')
    def _compute_payment_date(self):
        for data in self:
            payment_date =  False
            reconciled_partials = data._get_all_reconciled_invoice_partials()
            if reconciled_partials:
                aml_ids = [i['aml'].id for i in reconciled_partials]
                payments = self.env['account.move.line'].browse(aml_ids).mapped('payment_id') 
                if payments:
                    payment_date = sorted(payments, key=lambda x: x['date'], reverse=True)[0]['date']
            data.payment_date = payment_date