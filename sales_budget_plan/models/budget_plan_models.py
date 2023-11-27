# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class sales_budget_plan(models.Model):
    _name = 'sale.sales_budget_plan'
    _description = 'Budget Plan'

    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        help="If not set, the budget will apply to all variants of this products.")
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade', oldname='product_id')
    date_start = fields.Date('Start Date', help="Start date for this budget")
    date_end = fields.Date('End Date', help="End date for this budget")
    user_id = fields.Many2one(
             'res.users',
             string='Responsible',
             default=lambda self: self.env.user)
    budget = fields.Float(
        'Budget', default=0.0, digits=dp.get_precision('Product Price'),
        required=True, help="The price to purchase a product")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id, index=1)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    is_active = fields.Boolean('Active', default=True)

#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
