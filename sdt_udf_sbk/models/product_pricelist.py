
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime, formatLang



class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"


    product_tmpl_id = fields.Many2one(domain=[('sale_ok','=',True)])