from datetime import datetime

from odoo import models, fields,api


class Invoice(models.Model):
    _inherit = "account.invoice"
    _description = "Account Invoice"

    def walking_cust(self):
        res = self.env['res.partner'].search([('name','=','Walk-in Customer')],limit=1)
        return res
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always', ondelete='restrict',
                                 help="You can find a contact by its Name, TIN, Email or Internal Reference.",default=walking_cust)
    fee_type = fields.Selection([('credit_debit_card','Credit/Debit Card'), ('nets', 'NETS'), ('grabpay', 'GrabPay'), ('shopeepay','ShopeePay')])
    fee_amount = fields.Float()
    total_cost = fields.Float("Total Cost",compute='totalcostcompute')
    add_total = fields.Float('Add Total')
    date_invoice = fields.Date(string='Invoice Date',
                               readonly=True, states={'draft': [('readonly', False)]}, index=True,
                               help="Keep empty to use the current date", copy=False,default=fields.Date.context_today)

    profit = fields.Float("Profit",compute='profitcomp')
    yearzz = fields.Integer("Year",store=True,compute = '_yearcompute')
    monthzz = fields.Integer('Month',store=True ,compute = '_yearcompute')
    week = fields.Integer("Week",store=True,compute = '_yearcompute')
    other_cost = fields.Float('Other cost')

    @api.depends('date_invoice')
    def _yearcompute(self):
        for rec in self:
            if rec.date_invoice:
              rec.yearzz =int(rec.date_invoice.year)
              rec.monthzz = int(rec.date_invoice.month)
              rec.week = int(rec.date_invoice.isocalendar()[1])
            else:
                rec.yearzz=0
                rec.monthzz=0
                rec.week = 0
                # rec.month = 0
                # rec.week = 0
            # rec.month = int(rec.date_invoice.month)
            # rec.week = int(rec.date_invoice.isocalendar()[1])

    @api.depends('total_cost','amount_untaxed','other_cost','fee_amount')
    def profitcomp(self):
        for rec in self:
            rec.profit = rec.amount_untaxed-rec.total_cost-rec.other_cost-rec.fee_amount



    @api.onchange('add_total')
    def pricetotal(self):
        for rec in self:
            if rec.invoice_line_ids:
                rec.invoice_line_ids[0].price_subtotal = rec.add_total
                for line in rec.invoice_line_ids[1:]:
                    line.price_subtotal = 0.0
            # total_line = len(rec.invoice_line_ids)
            # if rec.add_total > 0:
            #     total = rec.add_total - rec.amount_tax
            #     price_per = total / total_line
            #     for line in rec.invoice_line_ids:
            #         line.update({'price_unit': price_per / line.quantity})

    # @api.onchange('invoice_line_ids.product_cost')
    # def pricetotal_lin(self):
    #     for rec in self:
    #
    #         total_line = len(rec.invoice_line_ids)
    #         if rec.add_total > 0:
    #             total = rec.add_total - rec.amount_tax
    #             price_per = total / total_line
    #             for line in rec.invoice_line_ids:
    #                 line.update({'price_unit': price_per / line.quantity})

    @api.depends('invoice_line_ids')
    def totalcostcompute(self):
        for rec in self:
            cost_total = 0.0
            for line in rec.invoice_line_ids:
                cost_total=cost_total+line.product_cost
            rec.total_cost = cost_total

    @api.onchange('fee_type','amount_total')
    def fee_cal(self):
        for rec in self:
            print(rec.fee_type, rec.amount_total)
            if rec.fee_type == 'grabpay' or rec.fee_type == "shopeepay":
                rec.fee_amount = rec.amount_total / 100
                print("Fee=", rec.fee_amount)
            else:
                rec.fee_amount = 0



class InvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'
    _description = "Invoice Lines"

    product_cost = fields.Float('Product Cost')


    @api.onchange('product_id')
    def cost(self):
        self.product_cost = self.product_id.standard_price


class InvoiceFee(models.Model):
    _name = 'invoice.fee'
    _description = "Invoice Card Fee"

    def journal_default(self):
        res = self.env['account.journal'].search([('name','=','Credit Card Fees')],limit=1)
        return res

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default="draft")
    name = fields.Char()
    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'), ],
                             string='Month', default=1)
    year = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year) + 1)], 'Year',
                            default=datetime.now().year)
    fee_type = fields.Selection([('credit_debit_card', 'Credit/Debit Card'), ('nets', 'NETS'), ('grabpay', 'GrabPay'),
                                 ('shopeepay', 'ShopeePay')])
    remarks = fields.Text()
    journal_id = fields.Many2one('account.journal', string='Credit Card Fee Journal', required=True,
                                 domain=[('type', '=', 'general')], default=journal_default)
    move_id = fields.Many2one('account.move', string="Journal Entry")
    inv_lines = fields.One2many('invoice.fee.detail', 'card_fee_id')


    @api.onchange('month','year','fee_type')
    def get_invoice(self):
        inv = self.env["account.invoice"].search([('monthzz', '=', self.month),('yearzz','=',self.year),('state','=','paid'),('type','=','out_invoice'),('fee_amount', '=', 0)])
        if self.fee_type:
            inv = self.env["account.invoice"].search(
                [('monthzz', '=', self.month), ('yearzz', '=', self.year), ('fee_type', '=', self.fee_type), ('state', '=', 'paid'),('type','=','out_invoice'),('fee_amount', '=', 0)])
        inv_list = [(5, 0, 0)]

        for rec in inv:
            fee_amt=0
            if rec.fee_type == 'grabpay' or rec.fee_type == "shopeepay":
                fee_amt = rec.amount_total / 100

            inv_list.append((0, 0, {
                'invoice_no': rec.id,
                'fee_type': rec.fee_type,
                'invoice_amount': rec.amount_total,
                'fee_amount': fee_amt
            }))
        self.inv_lines = inv_list

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('fee.seq')
        return super(InvoiceFee, self).create(values)

    @api.multi
    def confirm(self):
        for rec in self.inv_lines:
            rec.invoice_no.write({'fee_amount': rec.fee_amount})
        self._create_general_entry()
        self.state = "confirm"

    @api.model
    def _create_general_entry(self):
        tot_fee = 0
        partner_id =0
        for rec in self.inv_lines:
            tot_fee = tot_fee + rec.fee_amount
            partner_id = rec.invoice_no.partner_id.id

        debit_vals={
            'account_id':self.journal_id.default_debit_account_id.id,
            'partner_id': partner_id,
            'invoice_id':  False,
            #'move_id': move.id,
            'debit': tot_fee,
            'credit': 0,
            'amount_currency':  False,
            #'payment_id': self.id,
            'journal_id': self.journal_id.id,
        }
        #deb = self.env['account.move.line'].new(debit_vals)

        credit_vals = {
            'account_id': self.journal_id.default_credit_account_id.id,
            'partner_id': partner_id,
            'invoice_id': False,
            #'move_id': move.id,
            'debit': 0,
            'credit': tot_fee,
            'amount_currency': False,
            #'payment_id': self.id,
            'journal_id': self.journal_id.id,
        }
        move_line_vals = []
        move_line_vals.append((0,0,debit_vals))
        move_line_vals.append((0, 0, credit_vals))
        move_vals = {
            'date': self.create_date,
            'ref': self.name,
            'company_id': self.journal_id.company_id.id,
            'journal_id': self.journal_id.id,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        }
        move = self.env['account.move'].create(move_vals)
        move.post()
        self.move_id = move.id

class InvoiceFeeDetail(models.Model):
    _name = "invoice.fee.detail"

    card_fee_id = fields.Many2one('invoice.fee')
    invoice_no = fields.Many2one('account.invoice')
    fee_type = fields.Selection(related="invoice_no.fee_type")
    invoice_amount = fields.Float()
    fee_amount = fields.Float()

    @api.onchange('invoice_no')
    def on_invoice_change(self):
        for rec in self:
            rec.invoice_amount = rec.invoice_no.amount_total
