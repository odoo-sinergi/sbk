from odoo import api, fields, models, time, _
from odoo.exceptions import Warning, UserError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class SBKBankStatementReport(models.TransientModel):
    _name = 'sbk.bank.statement.report.wiz'

    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date(default=fields.Date.today)
    s_balance = fields.Float(string="Starting Balance")
    e_balance = fields.Float(string="Ending Balance")
    statement_lines = fields.Many2many('sbk.bank.statement.detail', string="Statement Lines")

    @api.multi
    def run_process(self):
        whr_claus = " a.date>'"+str(self.start_date)+"' and a.date<'"+str(self.end_date)+"'"
        
        query = ''' Delete from sbk_bank_statement_detail;
                    select 
                        a.date,
                        a.name as label,
                        (select name from res_partner rp where rp.id=a.partner_id) as partner, 
                        a.ref,
                        (select scn.code || ' ' || scn.name as code_name from sbk_code_name scn where scn.id = a.code_name) as code_name,
                        CASE
                            WHEN a.amount<0 THEN a.amount*-1
                            ELSE 0
                        END 
                        AS debit,
                        CASE
                            WHEN a.amount>0 THEN a.amount*1
                            ELSE 0
                        END 
                        AS credit,
                        a.amount 
                    from account_bank_statement_line a
                    where''' + whr_claus + '''
                    group by a.date, a.name, a.partner_id, a.ref,a.amount,a.code_name
                    
        '''

        print(query)
        self._cr.execute(query)
        query_res = self._cr.dictfetchall()
        in_out_obj = self.env['sbk.bank.statement.detail']
        return_obj = self.env['sbk.bank.statement.detail']
        print(query_res)
        list_rec = []
        self.e_balance = self.s_balance
        for lines in query_res:
            self.e_balance = self.e_balance + lines['debit'] - lines['credit']
            nope = ""
            if str(lines['code_name']) == 'None':
                lines['code_name'] = nope
            in_out_obj = self.env['sbk.bank.statement.detail'].create({
                'date': lines['date'],
                'label': lines['label'],
                'partner': lines['partner'],
                'reference': lines['ref'],
                'code_name': lines['code_name'],
                'debit': lines['debit'],
                'credit': lines['credit'],
                'amount': self.e_balance,
            })
            list_rec.append(in_out_obj.id)
            return_obj += self.env['sbk.bank.statement.detail'].browse(in_out_obj.id)

        self.statement_lines = [(6, 0, list_rec)]
        return return_obj

    @api.multi
    def export_to_excel(self, data):
        return self.env.ref('sbk_bank_statement.sbs_excel_statement').report_action(self, data=data, config=False)

    @api.multi
    def form_close(self):
        return {'type': 'ir.actions.act_window_close'}


class ReportDetail(models.Model):
    _name = 'sbk.bank.statement.detail'

    date = fields.Char(readonly=True)
    label = fields.Char(readonly=True)
    partner = fields.Char(readonly=True)
    reference = fields.Char(readonly=True)
    code_name = fields.Char(readonly=True)
    debit = fields.Char(readonly=True)
    credit = fields.Char(readonly=True)
    amount = fields.Char(readonly=True)
