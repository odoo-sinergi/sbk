# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields
from odoo.tools.misc import formatLang, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_is_zero
from datetime import datetime, timedelta
from odoo.exceptions import UserError




class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.report"
    _name = "sale.ledger"
    _description = "Sale Summary Report"

    sum_colspan = 4
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_cash_basis = False
    filter_all_entries = False
    filter_unfold_all = False
    filter_account_type = [{'id': 'receivable', 'name': _('Receivable'), 'selected': False}, {'id': 'payable', 'name': _('Payable'), 'selected': False}]
    filter_unreconciled = False
    #TODO add support for partner_id
    filter_partner_id = False


    @api.multi
    def open_document(self, options, params=None):
        # raise UserError('akkkakak')
        if not params:
            params = {}
        ctx = self.env.context.copy()
        # raise UserError(u'%s****%s'%(params, ctx))
        ctx.pop('id', '')
        aml_id = params.get('id')
        document = params.get('object', 'account.move')
        if aml_id:

            aml = self.env[document].browse(aml_id)
            view_name = 'view_order_line_form'
            res_id = aml.id
            view_id = self.env['ir.model.data'].get_object_reference('sbk_sol_report', view_name)[1]
            if document == 'account.invoice' and aml.invoice_id.id:
                res_id = aml.invoice_id.id
                if aml.invoice_id.type in ('in_refund', 'in_invoice'):
                    view_name = 'invoice_supplier_form'
                    ctx['journal_type'] = 'purchase'
                elif aml.invoice_id.type in ('out_refund', 'out_invoice'):
                    view_name = 'invoice_form'
                    ctx['journal_type'] = 'sale'
                ctx['type'] = aml.invoice_id.type
                ctx['default_type'] = aml.invoice_id.type
                view_id = self.env['ir.model.data'].get_object_reference('account', view_name)[1]
            elif document == 'account.payment' and aml.payment_id.id:
                view_name = 'view_account_payment_form'
                res_id = aml.payment_id.id



                view_id = self.env['ir.model.data'].get_object_reference('account', view_name)[1]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'tree',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': document,
                'view_id': view_id,
                'res_id': res_id,
                'domain':[],
                # 'context': ctx,
            }



    # TODO: remove when https://github.com/odoo/odoo/pull/31211 is merged and _lt is used above
    def _build_options(self, previous_options=None):
        self.filter_account_type = [{'id': 'receivable', 'name': _('Receivable'), 'selected': False}, {'id': 'payable', 'name': _('Payable'), 'selected': False}]
        return super(ReportPartnerLedger, self)._build_options(previous_options=previous_options)

    def get_templates(self):
        templates = super(ReportPartnerLedger, self).get_templates()
        templates['line_template'] = 'sbk_sol_report.line_template_partner_ledger_report'
        templates['main_template'] = 'sbk_sol_report.template_partner_ledger_report'
        # templates['line_template'] = 'account_reports.line_template_partner_ledger_report'
        # templates['main_template'] = 'account_reports.template_partner_ledger_report'
        return templates

    def get_columns_name(self, options):
    
        return [
            {},
            {'name': _('Order Reference')},
            {'name': _('Customer')},
            {'name': _('Description')},
            {'name': _('Qty'), 'class': 'number'},
            {'name': _('Price Unit'), 'class': 'number'},
            {'name': _('Subtotal'), 'class': 'number'},
           
        ]



    def set_context(self, options):
        ctx = super(ReportPartnerLedger, self).set_context(options)
        ctx['strict_range'] = True
        return ctx

    def do_query(self, options, line_id):
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        # Create the currency table.
        user_company = self.env.user.company_id
        companies = self.env['res.company'].search([])
        rates_table_entries = []
        for company in companies:
            if company.currency_id == user_company.currency_id:
                rate = 1.0
            else:
                rate = user_company.currency_id.rate / company.currency_id.rate
            rates_table_entries.append((company.id, rate, user_company.currency_id.decimal_places))
        currency_table = ','.join('(%s, %s, %s)' % r for r in rates_table_entries)
        with_currency_table = 'WITH currency_table(company_id, rate, precision) AS (VALUES %s)' % currency_table

     
        context = self.env.context
        base_domain = self.base_domain_generator( context, options)

        # date_from = options['date']['date_from']
        # base_domain = [('create_date', '<=', context['date_to']), ('company_id', 'in', context['company_ids'])]
        # base_domain.append(('create_date', '>=', date_from))

        query = self.env['sale.order.line']._where_calc(base_domain)
        tables, where_clause, params = query.get_sql()

        price_sub_total_field = 'price_subtotal'
        product_uom_id_field = 'product_uom_qty'
        query = '''
            SELECT
                \"sale_order_line\".order_partner_id,
                SUM(ROUND(\"sale_order_line\".''' + price_sub_total_field + ''' * currency_table.rate, currency_table.precision))     AS price_subtotal,
                SUM(ROUND(\"sale_order_line\".''' + product_uom_id_field + ''' * currency_table.rate, currency_table.precision))    AS product_uom_qty
            FROM %s
            LEFT JOIN currency_table                    ON currency_table.company_id = \"sale_order_line\".company_id
            WHERE %s
            AND \"sale_order_line\".order_partner_id IS NOT NULL
            GROUP BY \"sale_order_line\".order_partner_id
        ''' % (tables, where_clause)

        

        if line_id:
            query = query.replace('WHERE', 'WHERE \"sale_order_line\".order_partner_id = %s AND')
            params = [str(line_id)] + params

       
        self._cr.execute(with_currency_table + query, params)
        
        
        query_res = self._cr.dictfetchall()
        print ('query_res***', query_res)
        rs = dict((res['order_partner_id'], res) for res in query_res)
        return rs
    

    def base_domain_generator1(self, context, options):
        date_from = options['date']['date_from']
        base_domain = [('create_date', '<=', context['date_to']), ('company_id', 'in', context['company_ids'])]
        base_domain.append(('create_date', '>=', date_from))
        return base_domain

    def base_domain_generator(self, context, options):
        rs = self.base_domain_generator1(context, options)
        rs +=[('price_unit','!=', 0)]
        return rs

    def group_by_partner_id(self, options, line_id):
        partners = {}
        results = self.do_query(options, line_id)
        context = self.env.context
        base_domain = self.base_domain_generator( context, options)
        for partner_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('order_partner_id', '=', partner_id))
            partner = self.env['res.partner'].browse(partner_id)
            partners[partner] = result
            # partners[partner]['initial_bal'] = initial_bal_results.get(partner.id, {'balance': 0, 'debit': 0, 'credit': 0})
            # partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
            if not context.get('print_mode'):
                #  fetch the 81 first amls. The report only displays the first 80 amls. We will use the 81st to know if there are more than 80 in which case a link to the list view must be displayed.
                partners[partner]['lines'] = self.env['sale.order.line'].search(domain, order='create_date', limit=81)
            else:
                partners[partner]['lines'] = self.env['sale.order.line'].search(domain, order='create_date')

        
        
        return partners


    def gen_data_line(self, line):
        return [line.order_id.name, line.order_partner_id.name, line.name, line.product_uom_qty, line.price_unit, line.price_subtotal]
        
    def gen_data_sum_line(self, grouped_partners, partner):
        price_subtotal = grouped_partners[partner]['price_subtotal']
        product_uom_qty = grouped_partners[partner]['product_uom_qty']
        return [product_uom_qty, '___', self.format_value(price_subtotal)]

    @api.model
    def get_lines(self, options, line_id=None):
        lines = []
        if line_id:
            line_id = line_id.replace('partner_', '')
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id

        #If a default partner is set, we only want to load the line referring to it.
        if options.get('partner_id'):
            line_id = options['partner_id']

        grouped_partners = self.group_by_partner_id(options, line_id)
        sorted_partners = sorted(grouped_partners, key=lambda p: p.name or '')
        unfold_all = context.get('print_mode') and not options.get('unfolded_lines') or options.get('partner_id')
        total_initial_balance = total_debit = total_credit = total_balance = 0.0
        for partner in sorted_partners:
            lines.append({
                'id': 'partner_' + str(partner.id),
                'name': partner.name,
                'columns': [{'name': v} for v in self.gen_data_sum_line(grouped_partners, partner)],
                'level': 2,
                'trust': partner.trust,
                'unfoldable': True,
                'unfolded': 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all,
                'colspan': self.sum_colspan,
            })
            used_currency = self.env.user.company_id.currency_id
            if 1:#'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all:
                # progress = initial_balance
                domain_lines = []
                amls = grouped_partners[partner]['lines']
                too_many = False
                if len(amls) > 80 and not context.get('print_mode'):
                    amls = amls[:80]
                    too_many = True
                for line in amls:
                    domain_lines.append({
                        'id': line.id,
                        'parent_id': 'partner_' + str(partner.id),
                        # 'name': format_date(self.env, line.date),
                        'name':format_date(self.env, line.create_date),
                        'columns': [{'name': v} for v in self.gen_data_line(line) ],
                        'caret_options': 'sale.order.line',
                        'level': 4,
                    })
                if too_many:
                    domain_lines.append({
                        'id': 'too_many_' + str(partner.id),
                        'parent_id': 'partner_' + str(partner.id),
                        'action': 'view_too_many',
                        'action_id': 'partner,%s' % (partner.id,),
                        'name': _('There are more than 80 items in this list, click here to see all of them'),
                        'colspan': 8,
                        'columns': [{}],
                    })
                lines += domain_lines
        if not line_id:
            lines.append({
                'id': 'grouped_partners_total',
                'name': _('Total'),
                'level': 0,
                'class': 'o_account_reports_domain_total',
                'columns': [{'name': v} for v in ['', '', '', '', self.format_value(total_initial_balance), self.format_value(total_debit), self.format_value(total_credit), self.format_value(total_balance)]],
            })
    
        return lines

    @api.model
    def get_report_name(self):
        return _('Sale Summary Report')

class ReportPartnerSample(models.AbstractModel):
    _inherit = "sale.ledger"
    _name = "sample.ledger"
    _description = "Sample"
    sum_colspan = 4
    def get_columns_name(self, options):
        return [
            {},
            {'name': _('Order Reference')},
            {'name': _('Customer')},
            {'name': _('Description')},
            {'name': _('Qty'), 'class': 'number'},
            # {'name': _('Price Unit'), 'class': 'number'},
            {'name': _('Subtotal'), 'class': 'number'},
        ]

    def base_domain_generator(self, context, options):
        rs = self.base_domain_generator1(context, options)
        rs +=[('price_unit','=', 0)]
        return rs
    def gen_data_line(self, line):
        return [line.order_id.name, line.order_partner_id.name, line.name, line.product_uom_qty, line.price_subtotal]

    def gen_data_sum_line(self, grouped_partners, partner):
        price_subtotal = grouped_partners[partner]['price_subtotal']
        product_uom_qty = grouped_partners[partner]['product_uom_qty']
        return [product_uom_qty, self.format_value(price_subtotal)]

    @api.model
    def get_report_name(self):
        return _('Sample Summary Report')
