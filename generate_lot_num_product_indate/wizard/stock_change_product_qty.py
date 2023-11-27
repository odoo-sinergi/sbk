from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import date


class ProductChangeQuantity(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    @api.one
    @api.constrains('lot_id')
    def check_lot_id(self):
        print('check QUANTITY')
        if self.lot_id and self.product_id.tracking == 'lot' and date.today() != fields.Date.from_string(self.lot_id.create_date):
            raise ValidationError(
                _('Please choose different Lot Number since stock in date is not today.'))
