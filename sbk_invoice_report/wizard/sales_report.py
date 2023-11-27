from odoo import models, fields, api, time, _
from odoo.exceptions import Warning, UserError
from datetime import datetime
import calendar

import logging
_logger = logging.getLogger(__name__)


class InvoiceReport(models.TransientModel):
    _name = 'invoice.report.wiz'

    date_from = fields.Date(required=1)
    date_to = fields.Date(required=1)
    
    customer = fields.Many2one('res.partner', string='Customer')

    
    invoice_lines = fields.Many2many('invoice.report.lines', string="Sales Report Lines")

    @api.multi
    def run_process(self):
        
        so = self.env['account.invoice'].search([('date_invoice', '>=', self.date_from),('date_invoice', '<=', self.date_to),('state', 'not in', ['draft','cancel'])])
        # so = self.env['account.invoice'].search([])

        list_rec = []
        return_obj = self.env['invoice.report.lines']
        for line in so:
            in_out_obj = self.env['invoice.report.lines'].create({
                'invoice_number': line.number,
                'customer_name': line.partner_id.name,
                'date': line.date_invoice,
                'freight': line.freight,
                'amount_tax': line.amount_tax,
                'amount_total': line.amount_total,
                'amount_untaxed': line.amount_untaxed,

            })
            list_rec.append(in_out_obj.id)
            return_obj += self.env['invoice.report.lines'].browse(in_out_obj.id)

        self.invoice_lines = [(6, 0, list_rec)]
        return return_obj

    @api.multi
    def print_report(self):
        return self.env.ref('sbk_invoice_report.action_invoice_report').report_action(self)

    # @api.multi
    # def export_to_excel(self, data):
    #     return self.env.ref('teeni_crm.sales_report_excel').report_action(self, data=data, config=False)

    @api.multi
    def form_close(self):
        return {'type': 'ir.actions.act_window_close'}

class InvoiceReportLines(models.Model):
    _name = 'invoice.report.lines'

    invoice_number = fields.Char(readonly=True)
    customer_name = fields.Char(readonly=True)
    date = fields.Date(readonly=True)
    freight = fields.Float()
    amount_tax = fields.Float()
    amount_total = fields.Float()
    amount_untaxed  = fields.Float()
