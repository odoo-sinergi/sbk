from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_default_code = fields.Char(
        'Internal Reference', related='product_id.default_code', store=True)
