from odoo import api, fields, models
from datetime import date
import datetime
from odoo.exceptions import UserError
class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    name = fields.Char(
        'Lot/Serial Number', compute='_generate_lot_num', store=True, help="Unique Lot/Serial Number", readonly=0)
    register_date = fields.Date(default=fields.Date.today)

    # @api.one
    # @api.depends('product_id', 'create_date')
    # def _generate_lot_num(self):
    #     if self.product_id:
    #         tracking = self.product_id.tracking
    #         if tracking == 'lot' and self.product_id.barcode:
    #             self.name = self.product_id.barcode + '-' + \
    #                 str(date.today())
    #         else:
    #             self.name = self.product_id.name + '_' + \
    #                 self.env['ir.sequence'].next_by_code('stock.lot.serial')
    #     else:
    #         self.name = self.env['ir.sequence'].next_by_code(
    #             'stock.lot.serial')

    @api.one
    @api.depends('product_id', 'register_date')
    def _generate_lot_num(self):
        if self.product_id:
            tracking = self.product_id.tracking
            print ('*****',tracking == 'lot',self.product_id.barcode )
            if tracking == 'lot' and self.product_id.barcode:
                self.name = self.product_id.barcode + '-' + \
                    self.register_date
            else:
                self.name = self.product_id.name + '_' + \
                    self.env['ir.sequence'].next_by_code('stock.lot.serial')
        else:
            self.name = self.env['ir.sequence'].next_by_code(
                'stock.lot.serial')
class StockInventory(models.Model):
    _inherit = 'stock.inventory'
    def action_done(self):
        in_date_inventory = fields.Datetime.from_string(self.date)
        rs =  super(StockInventory,self.with_context(in_date_inventory = in_date_inventory)).action_done()
        return rs


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    def update_context_in_date(self,kwargs):
        in_date_inventory = self._context.get('in_date_inventory', None)
        kwargs.update({'in_date': in_date_inventory})

    @api.model
    def _update_available_quantity(self,*args,**kwargs):
        self.update_context_in_date(kwargs)
        return super(StockQuant, self)._update_available_quantity(*args,**kwargs)

    @api.model
    def _update_reserved_quantity(self, *args,**kwargs):
        return super(StockQuant, self)._update_reserved_quantity(*args,**kwargs)
