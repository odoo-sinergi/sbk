# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError



class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_order_line_count = fields.Integer(compute='_compute_sale_order_line_count', string='# of Sales Order')
    sample_sale_order_line_count = fields.Integer(compute='_compute_sample_sale_order_line_count', string='# of Sales Order')
    
    def _compute_sale_order_line_count(self):
        for r in self:
            rs = self.env['sale.order.line'].search_count([('order_partner_id','=', r.id), ('price_unit','!=', 0)])
            r.sale_order_line_count = rs

    def _compute_sample_sale_order_line_count(self):
        for r in self:
            rs = self.env['sale.order.line'].search_count([('order_partner_id','=', r.id), ('price_unit','=', 0), ('price_unit','=', 0)])
            r.sample_sale_order_line_count = rs
            
    

    def open_sample_ledger(self):
        return {'type': 'ir.actions.client',
            'name': _('Sample Summary'),
            'tag': 'account_report',
            'options': {'partner_id': self.id},
            'ignore_session': 'both',
            'context': "{'model':'sample.ledger'}"}


    def open_sale_ledger(self):
        return {'type': 'ir.actions.client',
            'name': _('Sale Summary'),
            'tag': 'account_report',
            'options': {'partner_id': self.id},
            'ignore_session': 'both',
            'context': "{'model':'sale.ledger'}"}

    def open_crm_ledger(self):
        return {'type': 'ir.actions.client',
            'name': _('Crm Summary'),
            'tag': 'account_report',
            'options': {'partner_id': self.id},
            # 'ignore_session': 'both',
            'context': "{'model':'crm.ledger'}"}









    