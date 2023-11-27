from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InvoiceSummary(models.TransientModel):
    _name = 'invoice.summary.wiz'
    _description = 'Invoice Summary Report Wiz'

    date_from = fields.Date("Date From",required=True)
    date_to = fields.Date("Date To",required=True)
    @api.constrains('date_from','date_to')
    def _datevalidation(self):
        if self.date_to< self.date_from:
            raise ValidationError(_("Date To Must b greater or equal to Date From"))
    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env.ref('invoice.action_bank_account_report').report_action(self, data=data,config=False)