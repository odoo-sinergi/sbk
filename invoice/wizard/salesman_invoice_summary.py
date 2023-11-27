from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class SalesManInvoiceSummary(models.TransientModel):
    _name = 'saleman.invoice.summary.wiz'
    _description = 'Invoice Summary Report Wiz'

    # def get_years(self):
    #     year_list = []
    #     for i in range(2016, 2036):
    #         year_list.append((i, str(i)))
    #     return year_list
    # def get_week(self):
    #     week_lst = []
    #     for i in range(1, 52):
    #         week_lst.append((i, str(i)))
    #     return week_lst

    report_type = fields.Selection([('month','Month'),('week','Week')],default='month')
    sale_person = fields.Many2many('res.users',String="Salepersons",required=True)
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                          (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                          (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'), ],
                          string='Month',default=1)
    year =  fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Year',default = datetime.now().year)
    week =fields.Selection([(num, str(num)) for num in range(1,52)],"Week")
    # date_from = fields.Date("Date From",required=True)
    # date_to = fields.Date("Date To",required=True)
    # @api.constrains('date_from','date_to')
    # def _datevalidation(self):
    #     if self.date_to< self.date_from:
    #         raise ValidationError(_("Date To Must b greater or equal to Date From"))

    @api.onchange('report_type')
    def reporttpye(self):
        for rec in self:
            if rec.report_type == 'month':
                rec.week=''
            else:
                rec.month = ''

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['year', 'week','month','report_type'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['year', 'week','month','report_type'])[0])
        return self.env.ref('invoice.action_saleman_report').report_action(self, data=data,config=False)