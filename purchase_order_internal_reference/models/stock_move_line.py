from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_default_code = fields.Char(
        'Internal Reference', related='product_id.default_code', store=True)
