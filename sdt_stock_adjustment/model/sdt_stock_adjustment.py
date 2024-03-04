import uuid

from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

SESSION_STATES =[('open','Open'),('close','Close')]

def _get_default_name(self):
    return self.env['ir.sequence'].next_by_code('sdt.stock.adjustment')

class StockAdjustment(models.Model):
    _name = 'sdt.stock.adjustment'

    name = fields.Char('Inventory Reference',required='True')
    date = fields.Datetime('Inventory Date', required=True, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    accounting_date = fields.Date('Accounting Date', required=True, default=lambda self: time.strftime("%Y-%m-%d"))
    location_id = fields.Many2one('stock.location', 'Inventoried Location', required=True)
    is_active=fields.Boolean(string='Active')
    state = fields.Selection(string='State', selection=SESSION_STATES, required=False, readonly=True,default=SESSION_STATES[0][0])
    detail_ids=fields.One2many('sdt.stock.adjustment.details', 'adjustment_id', string='Detail Stock Adjustment', copy=True, readonly=True,)

    def add_adjustment(self,ntotal):
        sql_query = """select * from sdt_stock_adjustment where state='open' and is_active='Y' limit %s
                """
        self.env.cr.execute(sql_query,(ntotal,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            for res in result:
                location_id = res['location_id']
                inventory_date = res['date']
                accounting_date = res['accounting_date']
                adj_obj = self.env['sdt.stock.adjustment'].browse(res['id'])
                for line in adj_obj.detail_ids:
                    new_lines = self.env['stock.quant']
                    if line.product_id.tracking != 'none' and not line.lot_name:
                        raise UserError('Lot/Serial Number can not be empty [%s]' %(line.product_id.name))
                    if line.lot_name:
                        lot_id = self.env['stock.lot'].search([('name','=',line.lot_name),('product_id','=',line.product_id.id),('company_id','=',self.env.user.company_id.id)]).id
                        if not lot_id:
                            lot_id = self.env['stock.lot'].sudo().create({
                                'name':line.lot_name,
                                'product_id':line.product_id.id,
                                'company_id':self.env.user.company_id.id,
                                }).id
                        new_lines = self.env['stock.quant'].new({
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'location_id': location_id,
                            'lot_id': lot_id,
                            'inventory_date': inventory_date,
                            'inventory_quantity': line.quantity,
                            'inventory_diff_quantity': line.quantity,
                            'accounting_date': accounting_date,
                        })
                    else:
                        new_lines = self.env['stock.quant'].new({
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'location_id': location_id,
                            'inventory_date': inventory_date,
                            'inventory_quantity': line.quantity,
                            'inventory_diff_quantity': line.quantity,
                            'accounting_date': accounting_date,

                        })
                    new_lines.with_context(sdt_stock_adjustment_id=adj_obj.id).action_apply_inventory()
                    line.inv_id = new_lines.id
                if adj_obj.detail_ids:
                    adj_obj.write({'state':'close','is_active':False})


    def button_active(self):
        for data in self:
            if data.state=='open':
                if data.is_active==False:
                    data.is_active=True
                else:
                    data.is_active=False


class StockAdjustmentDetails(models.Model):
    _name = 'sdt.stock.adjustment.details'
    _order = "id desc, product_id desc"
    _rec_names_search = ['adjustment_id','product_id']

    adjustment_id = fields.Many2one(
        comodel_name='sdt.stock.adjustment',
        string='Adjustment Id', ondelete='cascade', required=True, index=True, copy=False, auto_join=True, check_company=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    barcode = fields.Char('Barcode',related='product_id.barcode',store=True)
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    tracking = fields.Selection(related='product_id.tracking')
    lot_name = fields.Char('Lot/Serial Number')
    quantity = fields.Float('Quantity')
    inv_id = fields.Many2one('stock.quant', 'Inventory Adjustment',readonly=True)



    @api.onchange('product_id')
    def prod_id_change(self):
        if not self.product_id:
            return {'domain': {'product_id': []}}
        self.product_uom_id=self.product_id.product_tmpl_id.uom_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        uom_id = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)]).uom_id
        uom_list = []
        if uom_id:
            for uom in uom_id:
                uom_list.append(uom.id)

        domain = {'product_uom_id': [('id', '=', uom_list)]}
        return {'domain': domain}
