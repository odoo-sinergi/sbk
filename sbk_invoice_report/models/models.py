# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta
import logging
import pytz


_logger = logging.getLogger(__name__)

def int_to_Roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
        ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
        ]
    roman_num = ''
    i = 0
    while  num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

# class IrSequenceDateRange(models.Model):
#     _inherit = 'ir.sequence.date_range'
#     def _next(self):
#         return super(IrSequenceDateRange, self.with_context(ir_sequence_date_range=None))._next()


class IrSequence(models.Model):
    _inherit = "ir.sequence"
    use_current_date = fields.Boolean(default=1, help="user current date not use fist date in range_date")

    alpha_a = ""


    def _get_prefix_suffix(self):
        def _interpolate(s, d):
            return (s % d) if s else ''

        def _interpolation_dict():
            print ('***self._context**', self._context)
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            print ('***range_date 1**', range_date)
            # Extract account.invoice and add A;
            try:
                if self._context.get('invoice'):
                    alter_account_invoice = self._context.get('invoice')
                    self.alpha_a = "A" if alter_account_invoice['amount_tax'] <= 0 else ""
            except ValueError:
                raise UserError("Failed to get the invoice in current context, please try again")
            if self._context.get('ir_sequence_date'):
                effective_date = datetime.strptime(self._context.get('ir_sequence_date'), '%Y-%m-%d')
            if not self.use_current_date and self._context.get('ir_sequence_date_range'):
                range_date = datetime.strptime(self._context.get('ir_sequence_date_range'), '%Y-%m-%d')
                print ('***range_date 2**', range_date)

            sequences = {
                'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key, format in sequences.items():
                val = effective_date.strftime(format)
                res[key] = val
                # val = range_date.strftime(format)
                if key =='month': #and self.use_current_date
                    val_roman_month = int_to_Roman(int(val))
                    res['roman_month'] = val_roman_month
                res['range_' + key] = range_date.strftime(format)

                res['current_' + key] = now.strftime(format)
            return res

        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % (self.get('name')))
        # Concatenating "A" in current suffix;
        interpolated_suffix = interpolated_suffix + self.alpha_a
        return interpolated_prefix, interpolated_suffix


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    picking_ids = fields.Many2many('stock.picking', compute='picking_ids_', store = False)
    proforma_number = fields.Char()
    estimated_freight = fields.Float(string="Estimated Freight")
    say = fields.Text(compute='amount_to_text_new')
    description = fields.Text()

    @api.depends('amount_total')
    def amount_to_text_new(self):
        for rec in self:
            if rec.amount_total:
                rec.say = rec.currency_id.with_context(lang=rec.partner_id.lang or 'es_ES').amount_to_text(rec.amount_total).upper()
            print(rec.say)
    
    @api.depends()
    def picking_ids_(self):
        for r in self:
            r.picking_ids = self.env['stock.picking'].search([('origin','!=',False),('origin','=', r.name)])

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['proforma_number'] = self.env['ir.sequence'].next_by_code('sbk_invoice_report.proforma') or _('New')
        return super(SaleOrder, self).create(vals)

    @api.onchange('id')
    def _get_quotation_number(self):
        if self.proforma_number:
            _logger.debug("PROFORMAFDFDFDF %s", self.proforma_number)
            self.quotation_number = self.proforma_number.replace('PI', 'Q')
        _logger.debug("QUOTTATION %s", self.quotation_number)

    quotation_number = fields.Char(compute='_get_quotation_number')

    # To fix unneccessary zero's from values, use this method;
    @api.multi
    def parse_num(self, num):
        val = str(num)
        integer, decimals = val.split('.') if '.' in val else (val, None)
        if decimals in ('0', None):
            return integer
        else:
            return val

    @api.onchange('estimated_freight')
    def freight_onchage_(self):
        self.amount_total = self.amount_untaxed + self.amount_tax + self.estimated_freight
        self.amount_total = self.parse_num(self.amount_total)
        self.amount_untaxed = self.parse_num(self.amount_untaxed)
        self.estimated_freight = self.parse_num(self.estimated_freight)


class Invoice(models.Model):
    _inherit = 'account.invoice'
    description = fields.Text()
    say = fields.Text(compute='amount_to_text_new')
    picking_ids = fields.Many2many('stock.picking', compute='picking_ids_', store = False)
    # e_commerce_invoice_no = fields.Char()
    # freight = fields.Float(string="Freight")
    @api.depends()
    def picking_ids_(self):
        for r in self:
            r.picking_ids = self.env['stock.picking'].search([('origin','!=',False),('origin','=', r.origin)])

    @api.depends('amount_total')
    def amount_to_text_new(self):
        for rec in self:
            if rec.amount_total:
                rec.say = rec.currency_id.with_context(lang=rec.partner_id.lang or 'es_ES').amount_to_text(rec.amount_total).upper()



