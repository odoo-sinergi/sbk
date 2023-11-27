from odoo import api, fields, models


class ModuleName(models.Model):
    _inherit = 'purchase.order.line'

    product_default_code = fields.Char(
        'Internal Reference', related='product_id.default_code', store=True)
