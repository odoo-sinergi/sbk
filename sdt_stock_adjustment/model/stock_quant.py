from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)



class StockQuant(models.Model):
    _inherit = 'stock.quant'


    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(qty, location_id, location_dest_id, out=False)
        if self._context.get('sdt_stock_adjustment_id',False):
            adj_obj = self.env['sdt.stock.adjustment'].browse(self._context.get('sdt_stock_adjustment_id',[]))
            res.update({'name':adj_obj.name})
        return res