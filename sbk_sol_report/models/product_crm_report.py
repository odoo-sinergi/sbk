# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from odoo import models, api, _, fields
from odoo.tools.misc import formatLang, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_is_zero
from datetime import datetime, timedelta
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.report"
    _name = "crm.ledger"
    _description = "CRM product report"

    sum_colspan = 2
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_cash_basis = False
    filter_all_entries = False
    filter_unfold_all = False
    filter_account_type = [{'id': 'receivable', 'name': _('Receivable'), 'selected': False}, {'id': 'payable', 'name': _('Payable'), 'selected': False}]
    filter_unreconciled = False
    #TODO add support for partner_id
    filter_partner_id = False
    # @api.multi
    # def get_report_informations(self, options):
    #     rs = super(ReportPartnerLedger, self).get_report_informations(options)
    #     rs['footnotes'] = [{'id': 1, 'line':'False', 'text': ''}]
    #     return rs
        


    # @api.multi
    # def open_document(self, options, params=None):
    #     # raise UserError('akkkakak')
    #     if not params:
    #         params = {}
    #     ctx = self.env.context.copy()
    #     ctx.pop('id', '')
    #     aml_id = params.get('id')
    #     document = params.get('object', 'account.move')
    #     if aml_id:

    #         aml = self.env[document].browse(aml_id)
    #         view_name = 'view_order_line_form'
    #         res_id = aml.id
    #         view_id = self.env['ir.model.data'].get_object_reference('sbk_sol_report', view_name)[1]
    #         if document == 'account.invoice' and aml.invoice_id.id:
    #             res_id = aml.invoice_id.id
    #             if aml.invoice_id.type in ('in_refund', 'in_invoice'):
    #                 view_name = 'invoice_supplier_form'
    #                 ctx['journal_type'] = 'purchase'
    #             elif aml.invoice_id.type in ('out_refund', 'out_invoice'):
    #                 view_name = 'invoice_form'
    #                 ctx['journal_type'] = 'sale'
    #             ctx['type'] = aml.invoice_id.type
    #             ctx['default_type'] = aml.invoice_id.type
    #             view_id = self.env['ir.model.data'].get_object_reference('account', view_name)[1]
    #         elif document == 'account.payment' and aml.payment_id.id:
    #             view_name = 'view_account_payment_form'
    #             res_id = aml.payment_id.id
    #             view_id = self.env['ir.model.data'].get_object_reference('account', view_name)[1]
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'tree',
    #             'view_mode': 'form',
    #             'views': [(view_id, 'form')],
    #             'res_model': document,
    #             'view_id': view_id,
    #             'res_id': res_id,
    #             'domain':[],
    #             # 'context': ctx,
    #         }



    # TODO: remove when https://github.com/odoo/odoo/pull/31211 is merged and _lt is used above
    # def _build_options(self, previous_options=None):
    #     self.filter_account_type = [{'id': 'receivable', 'name': _('Receivable'), 'selected': False}, {'id': 'payable', 'name': _('Payable'), 'selected': False}]
    #     return super(ReportPartnerLedger, self)._build_options(previous_options=previous_options)

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
            {'name': _('Customer')},
            {'name': _('Quantity'), 'class': 'number'},
            {'name': _('UOM'), 'class': 'number'},
            {'name': _('Date of Enquiries ')},
            # {'name': _('d')},
            # {'name': _('Qty'), 'class': 'number'},
            # {'name': _('Price Unit'), 'class': 'number'},
            # {'name': _('Subtotal'), 'class': 'number'},
           
        ]



    def set_context(self, options):
        ctx = super(ReportPartnerLedger, self).set_context(options)
        ctx['strict_range'] = True
        return ctx

    def do_query(self, options, line_id):
        context = self.env.context
        base_domain = self.base_domain_generator( context, options)
        query = self.env['sbk_crm_product.crm.product.line']._where_calc(base_domain)
        tables, where_clause, params = query.get_sql()
        query = '''
            SELECT sbk_crm_product_crm_product_line.product_id, sum (sbk_crm_product_crm_product_line.qty) as sum_qty
            FROM %s
            WHERE %s
            AND \"sbk_crm_product_crm_product_line\".product_id IS NOT NULL
            GROUP BY \"sbk_crm_product_crm_product_line\".product_id
        ''' % (tables, where_clause)
        self._cr.execute(query, params)
        query_res = self._cr.dictfetchall()
        rs = dict((res['product_id'], res) for res in query_res)
        return rs
    

    def base_domain_generator1(self, context, options):
        date_from = options['date']['date_from']
        base_domain = [('create_date', '<=', context['date_to'])]
        base_domain.append(('create_date', '>=', date_from))
        return base_domain

    def base_domain_generator(self, context, options):
        rs = self.base_domain_generator1(context, options)
        return rs

    def group_by_product_id(self, options, line_id):
        partners = {}
        results = self.do_query(options, line_id)
        context = self.env.context
        base_domain = self.base_domain_generator( context, options)
        for product_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('product_id', '=', product_id))
            if context.get('active_ids', []):
                domain.append(('crm_id.partner_id', '=', context.get('active_ids', [])[0]))
            partners[product_id] = result
            if not context.get('print_mode'):
                partners[product_id]['lines'] = self.env['sbk_crm_product.crm.product.line'].search(domain, order='create_date', limit=81)
            else:
                partners[product_id]['lines'] = self.env['sbk_crm_product.crm.product.line'].search(domain, order='create_date')

            #_logger.warning("KNK REPORT RST : %s",context.get('active_ids', []))
            if(len(partners[product_id]['lines'])==0):
                del partners[product_id]
        
        
        return partners


    def gen_data_line(self, line):
        customer_name = line.crm_id.partner_id.name
        date = fields.Datetime.from_string(line.enquiry_date).strftime('%Y-%d-%m')
        return [customer_name, line.qty, line.product_id.uom_id.name, date]
        
    def gen_data_sum_line(self, result):
        return [result['sum_qty'],'']


    @api.model
    def get_lines(self, options, line_id=None):
        lines = []
        if line_id:
            line_id = line_id.replace('partner_', '')
        context = self.env.context
        # company_id = context.get('company_id') or self.env.user.company_id

        #If a default partner is set, we only want to load the line referring to it.
        if options.get('partner_id'):
            line_id = options['partner_id']

        grouped_products = self.group_by_product_id(options, line_id)
        # sorted_partners = grouped_products
        # sorted_partners = sorted(grouped_products, key=lambda p: p.name or '')
        unfold_all = context.get('print_mode') and not options.get('unfolded_lines') or options.get('partner_id')
        # total_initial_balance = total_debit = total_credit = total_balance = 0.0
        total = 0
        for product in grouped_products:
            total +=grouped_products[product]['sum_qty']
            lines.append({
                'id': 'partner_' + str(product),
                'name': self.env['product.product'].browse(product).name,
                'columns': [{'name': v} for v in self.gen_data_sum_line(grouped_products[product])],
                'level': 2,
                # 'trust': partner.trust,
                'unfoldable': True,
                'unfolded': 'partner_' + str(product) in options.get('unfolded_lines') or unfold_all,
                'colspan': self.sum_colspan,
            })
            domain_lines = []
            amls = grouped_products[product]['lines']
            too_many = False
            if len(amls) > 80 and not context.get('print_mode'):
                amls = amls[:80]
                too_many = True
            for line in amls:
                domain_lines.append({
                    'id': line.id,
                    'parent_id': 'partner_' + str(product),
                    # 'name':format_date(self.env, line.create_date),
                    'name':'',
                    'columns': [{'name': v} for v in self.gen_data_line(line) ],
                    'caret_options': 'sale.order.line',
                    'level': 4,
                })
            if too_many:
                domain_lines.append({
                    'id': 'too_many_' + str(product),
                    'parent_id': 'partner_' + str(product),
                    'action': 'view_too_many',
                    'action_id': 'partner,%s' % (product,),
                    'name': _('There are more than 80 items in this list, click here to see all of them'),
                    'colspan': 8,
                    'columns': [{}],
                })
            lines += domain_lines
        # if not line_id:
        lines.append({
            'id': 'grouped_products_total',
            'name': _('Total'),
            'level': 0,
            'class': 'o_account_reports_domain_total',
            'columns': [{'name': v} for v in ['', total, '']],
        })
    
        return lines

    @api.model
    def get_report_name(self):
        return _('CRM Summary')