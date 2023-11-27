from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import date


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.constrains('lot_id')
    def _check_lot_id_create_date(self):
        for ml in self:
            if ml.picking_id and ml.picking_id.picking_type_id and ml.picking_id.picking_type_id.code == 'incoming' and ml.lot_id and ml.product_id.tracking == 'lot' and date.today() != fields.Date.from_string(ml.lot_id.create_date):
                raise ValidationError(
                    _('A lot number should only be linked to stocks that share the same stock-in-date.'))
