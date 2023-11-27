from odoo import api, fields, models, _



class ReportBankAccount(models.AbstractModel):
    _name = 'report.invoice.inv_summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        inv_data = []
        total_profit = 0.0
        total_cost = 0.0
        total_inv_amount = 0.0
        total_tax = 0.0

        invoice = self.env['account.invoice'].search([('date_invoice', '>=', docs.date_from),('date_invoice', '<=', docs.date_to),('type','=','out_invoice')])

        for inv in invoice:
            week = inv.date_invoice.isocalendar()[1]
            print(week,"week")
            total_profit+=inv.profit
            total_inv_amount+=inv.amount_untaxed
            total_tax+=inv.amount_tax
            special_cost = 0.0

            line_lst = []
            for line in inv.invoice_line_ids:
                total_cost+=line.product_cost
                special_cost+=line.product_id.product_tmpl_id.special_cost_price
                print(special_cost)
                product_cost = {
                    'product_cost': line.product_cost
                }
                line_lst.append(product_cost)
            invoice_dict = {
                'name':inv.number,
                'products_cost':line_lst,
                'tax':inv.amount_tax,
                'special_cost':special_cost,
                'invoice_amount':inv.amount_untaxed,
                'total_cost':inv.total_cost,
                'other_cost':inv.other_cost,
                'fee_amount':inv.fee_amount,
                'profit':inv.profit
            }
            inv_data.append(invoice_dict)

        amount_incl_taxes = total_inv_amount+total_tax

        return {
                'docs': docs,
                'inv_data': inv_data,
                'total_profit':round(total_profit,2),
                'total_cost':round(total_cost,2),

                'total_inv_amount':round(total_inv_amount,2),
                'total_tax':round(total_tax,2),
                 'amount_incl_taxes':round(amount_incl_taxes,2)
            }