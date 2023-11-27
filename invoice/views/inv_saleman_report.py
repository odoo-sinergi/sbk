from odoo import api, fields, models, _



class ReportBankAccount(models.AbstractModel):
    _name = 'report.invoice.inv_saleman_summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        inv_data = []
        total_profit = 0.0
        total_cost = 0.0
        total_inv_amount = 0.0
        total_tax = 0.0
        inv_lst = self.env['account.invoice']

        for user in docs.sale_person:
         single_user = []
         total_inv_amount = 0.0
         total_profit = 0.0
         total_tax = 0.0
         total_cost = 0.0
         if docs.report_type=='month':
             m = int(docs.month)
             invoice = self.env['account.invoice'].search([('monthzz', '=',m),('type','=','out_invoice'),('yearzz','=',int(docs.year)),('user_id','=',user.id)])
             inv_lst = invoice
         else:
             w = int(docs.week)
             print(w)
             invoice = self.env['account.invoice'].search([('week', '=',w),('type','=','out_invoice'),('yearzz','=',int(docs.year)),('user_id','=',user.id)])
             print(invoice,"WEeek")
             inv_lst = invoice
         user_dict={
             'name': user.name
         }
         for inv in inv_lst:
             total_inv_amount =total_inv_amount+ inv.amount_untaxed
             total_profit = total_profit+inv.profit
             total_tax = total_tax+inv.amount_tax
             total_cost = total_cost+inv.total_cost
             single_dict = {

                 'inv_no':inv.origin,
                 'amount_tax_ex':inv.amount_untaxed,
                 'tax':inv.amount_tax,
                 'total':inv.amount_untaxed,
                 'profit':inv.profit,
                 'other_cost': inv.other_cost,
                 'fee_amount': inv.fee_amount,
                 'total_cost':inv.total_cost
             }
             single_user.append(single_dict)
         user_dict.update({
             'invoices_data':single_user,
             'total_untaxed':total_inv_amount,
             'total_tax':total_tax,
             'total_include_tax':total_inv_amount+total_tax,
             'total_cost':total_cost,
             'total_profit':total_profit
         })
         inv_data.append(user_dict)

        return {
            'docs': docs,
            'inv_data':inv_data
        }
