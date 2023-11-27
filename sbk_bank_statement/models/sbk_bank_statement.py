from odoo.osv import expression
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SBKCodeName(models.Model):
    _name = "sbk.code.name"

    code = fields.Char(string="Code", required="True")

    name = fields.Char(string="Name")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for account in self:
            name = account.code + ' ' + account.name
            result.append((account.id, name))
        return result

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    code_name = fields.Many2one('sbk.code.name', string="Code/Name")

    debit = fields.Monetary(digits=0, currency_field='journal_currency_id', compute="_get_debit")

    credit = fields.Monetary(digits=0, currency_field='journal_currency_id', compute="_get_credit")

    def _get_debit(self):
        for line in self:
            if line.amount < 0: 
                line.debit = line.amount*-1
            else: line.debit = 0

    def _get_credit(self):
       for line in self:
            if line.amount > 0: 
                line.credit = line.amount
            else: line.credit = 0



