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


class StockAdjustment(models.Model):
    _name = 'sdt.stock.adjustment'
    
    name = fields.Char('Title', default='Draft', copy=False)
    reference = fields.Char('Reference', required='True', copy=False)
    date = fields.Datetime('Inventory Date', required=True, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    accounting_date = fields.Date('Accounting Date', required=True, default=lambda self: time.strftime("%Y-%m-%d"))
    location_id = fields.Many2one('stock.location', 'Inventoried Location', required=True)
    is_active=fields.Boolean(string='Active', copy=False)
    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company)
    state = fields.Selection(string='State', selection=SESSION_STATES, required=False, readonly=True, copy=False, default=SESSION_STATES[0][0])
    detail_ids=fields.One2many('sdt.stock.adjustment.details', 'adjustment_id', string='Detail Stock Adjustment', copy=True, readonly=True,)

    
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('sdt.stock.adjustment')

    # def add_adjustment(self,ntotal):
    #     sql_query = """select * from sdt_stock_adjustment where state='open' and is_active='Y' limit %s
    #             """
    #     self.env.cr.execute(sql_query,(ntotal,))
    #     result = self.env.cr.dictfetchall()
    #     if not result:
    #         return
    #     else:
    #         for res in result:
    #             location_id = res['location_id']
    #             inventory_date = res['date']
    #             accounting_date = res['accounting_date']
    #             adj_obj = self.env['sdt.stock.adjustment'].browse(res['id'])
    #             for line in adj_obj.detail_ids:
    #                 new_lines = self.env['stock.quant']
    #                 if line.product_id.tracking != 'none' and not line.lot_name:
    #                     raise UserError('Lot/Serial Number can not be empty [%s]' %(line.product_id.name))
    #                 if line.lot_name:
    #                     lot_id = self.env['stock.lot'].search([('name','=',line.lot_name),('product_id','=',line.product_id.id),('company_id','=',self.env.user.company_id.id)]).id
    #                     if not lot_id:
    #                         lot_id = self.env['stock.lot'].sudo().create({
    #                             'name':line.lot_name,
    #                             'product_id':line.product_id.id,
    #                             'company_id':self.env.user.company_id.id,
    #                             }).id
    #                     new_lines = self.env['stock.quant'].new({
    #                         'product_id': line.product_id.id,
    #                         'product_uom_id': line.product_uom_id.id,
    #                         'location_id': location_id,
    #                         'lot_id': lot_id,
    #                         'inventory_date': inventory_date,
    #                         'inventory_quantity': line.quantity,
    #                         'inventory_diff_quantity': line.quantity,
    #                         'accounting_date': accounting_date,
    #                     })
    #                 else:
    #                     new_lines = self.env['stock.quant'].new({
    #                         'product_id': line.product_id.id,
    #                         'product_uom_id': line.product_uom_id.id,
    #                         'location_id': location_id,
    #                         'inventory_date': inventory_date,
    #                         'inventory_quantity': line.quantity,
    #                         'inventory_diff_quantity': line.quantity_diff,
    #                         'accounting_date': accounting_date,

    #                     })
    #                 new_lines.with_context(sdt_stock_adjustment_id=adj_obj.id).action_apply_inventory()
    #                 line.inv_id = new_lines.id
    #             if adj_obj.detail_ids:
    #                 adj_obj.write({'state':'close','is_active':False})

    def add_adjustment(self,ntotal):
        sql_query = """select * from sdt_stock_adjustment where state='open' and is_active='Y' limit %s
                """
        self.env.cr.execute(sql_query,(ntotal,))
        result = self.env.cr.dictfetchall()
        if not result:
            return
        else:
            for res in result:
                inventory_date = res['date']
                adj_obj = self.env['sdt.stock.adjustment'].browse(res['id'])
                for line in adj_obj.detail_ids:
                    if line.quantity_diff > 0:
                        move_vals = line._get_inventory_move_values(line.quantity_diff,
                                                    line.product_id.with_company(line.adjustment_id.company_id).property_stock_inventory,
                                                    line.adjustment_id.location_id)
                    else:
                        move_vals = line._get_inventory_move_values(-line.quantity_diff,
                                                    line.adjustment_id.location_id,
                                                    line.product_id.with_company(line.adjustment_id.company_id).property_stock_inventory,
                                                    out=True)
                    move = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
                    move._action_done()
                    move.update({'date':inventory_date})
                    for move_line in move.move_line_ids:
                        move_line.update({'date':inventory_date})
                    for valuation in move.stock_valuation_layer_ids:
                        sql_query="""update stock_valuation_layer set create_date=%s where id=%s
                            """
                        self.env.cr.execute(sql_query,(inventory_date,valuation.id,))
                        for am in valuation.account_move_id:
                            am.update({'date':inventory_date})
                    line.move_id = move

                if adj_obj.detail_ids:
                    adj_obj.write({'state':'close','is_active':False})


    def button_active(self):
        for data in self:
            if data.state=='open':
                if data.name == 'Draft':
                    data.name = data._get_default_name()
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
    barcode = fields.Char('Barcode',related='product_id.barcode', store=True)
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    tracking = fields.Selection(related='product_id.tracking')
    lot_name = fields.Char('Lot/Serial Number')
    quantity = fields.Float(
        'Counted Quantity', digits='Product Unit of Measure',
        help="The product's counted quantity.")
    quantity_as_off = fields.Float(
        'Quantity as Of', compute='_compute_quantity_as_of', store=True,
        readonly=True, digits='Product Unit of Measure')
    quantity_diff = fields.Float(
        'Difference', compute='_compute_diff_quantity', store=True,
        help="Indicates the gap between the product's theoretical quantity and its counted quantity.",
        readonly=True, digits='Product Unit of Measure')
    inv_id = fields.Many2one('stock.quant', 'Inventory Adjustment', readonly=True)
    move_id = fields.Many2one('stock.move', 'Stock Move', readonly=True, copy=False)


    @api.depends('product_id','lot_name','adjustment_id.date','adjustment_id.location_id')
    def _compute_quantity_as_of(self):
        for line in self:
            if not line.product_id:
                line.quantity_as_off = 0
                continue
            
            lot_id = 0
            if line.lot_name:
                lot_id = self.env['stock.lot'].search([('name','=',line.lot_name),('product_id','=',line.product_id.id),('company_id','=',self.env.user.company_id.id)]).id
                if not lot_id:
                    lot_id = self.env['stock.lot'].sudo().create({
                        'name':line.lot_name,
                        'product_id':line.product_id.id,
                        'company_id':self.env.user.company_id.id,
                        }).id
            
            tz = self.env.user.tz
            if not tz:
                raise UserError('Timezone User [%s] can not be empty' %(self.env.user.display_name))
            date = line.adjustment_id.date or fields.Date.context_today(self)
            location_id = line.adjustment_id.location_id
            product_id = line.product_id
            company_id = line.adjustment_id.company_id
            
            if lot_id == 0:
                self._cr.execute(
                    """
                    SELECT sum(qty_done) as quantity
                    FROM stock_move_line
                    WHERE location_dest_id = %s and product_id = %s
                        and company_id = %s and state = 'done'
                        and cast(date ::timestamp at time zone 'UTC' AT time zone '""" + tz + """' as DATE) <= %s
                """,
                    (
                        location_id.id,
                        product_id.id,
                        company_id.id,
                        date
                    ),
                )
            else:
                self._cr.execute(
                    """
                    SELECT sum(qty_done) as quantity
                    FROM stock_move_line
                    WHERE location_dest_id = %s and product_id = %s and lot_id = %s
                        and company_id = %s and state = 'done'
                        and cast(date ::timestamp at time zone 'UTC' AT time zone '""" + tz + """' as DATE) <= %s
                """,
                    (
                        location_id.id,
                        product_id.id,
                        lot_id,
                        company_id.id,
                        date
                    ),
                )
            quants_in = self._cr.dictfetchone()
            if quants_in['quantity'] == None:
                quants_in['quantity'] = 0

            if lot_id == 0:
                self._cr.execute(
                    """
                    SELECT sum(qty_done) as quantity
                    FROM stock_move_line
                    WHERE location_id = %s and product_id = %s
                        and company_id = %s and state = 'done'
                        and cast(date ::timestamp at time zone 'UTC' AT time zone '""" + tz + """' as DATE) <= %s
                """,
                    (
                        location_id.id,
                        product_id.id,
                        company_id.id,
                        date
                    ),
                )
            else:
                self._cr.execute(
                    """
                    SELECT sum(qty_done) as quantity
                    FROM stock_move_line
                    WHERE location_id = %s and product_id = %s and lot_id = %s
                        and company_id = %s and state = 'done'
                        and cast(date ::timestamp at time zone 'UTC' AT time zone '""" + tz + """' as DATE) <= %s
                """,
                    (
                        location_id.id,
                        product_id.id,
                        lot_id,
                        company_id.id,
                        date
                    ),
                )
            quants_out = self._cr.dictfetchone()
            if quants_out['quantity'] == None:
                quants_out['quantity'] = 0

            line.quantity_as_off = quants_in['quantity'] - quants_out['quantity']

    @api.depends('quantity_as_off','quantity')
    def _compute_diff_quantity(self):
        for quant in self:
            quant.quantity_diff = quant.quantity - quant.quantity_as_off

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.adjustment_id.location_id:
            raise UserError('Inventoried Location can not be empty.')
        if not self.product_id:
            return
        
        self.product_uom_id = self.product_id.uom_id

        domain = {'product_uom_id': [('id', '=', self.product_id.uom_id.id)]}
        return {'domain': domain}
    
    def action_inventory_history(self):
        self.ensure_one()
        action = {
            'name': _('History'),
            'view_mode': 'list,form',
            'res_model': 'stock.move.line',
            'views': [(self.env.ref('stock.view_move_line_tree').id, 'list'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'context': {
                'search_default_inventory': 1,
                'search_default_done': 1,
                'search_default_product_id': self.product_id.id,
            },
            'domain': [
                ('move_id', '=', self.move_id.id),
            ],
        }
        
        return action
    
    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        """ Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param out: boolean to set on True when the move go to inventory adjustment location.
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        self.ensure_one()
        name = self.adjustment_id.name + ' - ' + self.product_id.display_name
        lot_id = self.env['stock.lot'].search([('name','=',self.lot_name),('product_id','=',self.product_id.id),('company_id','=',self.adjustment_id.company_id.id)])

        return {
            'name': self.env.context.get('inventory_name') or name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'company_id': self.adjustment_id.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'is_inventory': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.adjustment_id.company_id.id or self.env.company.id,
                'lot_id': lot_id.id,
                # 'package_id': out and self.package_id.id or False,
                # 'result_package_id': (not out) and self.package_id.id or False,
                # 'owner_id': self.owner_id.id,
            })]
        }
