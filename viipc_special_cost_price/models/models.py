import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    special_cost_price = fields.Monetary(string='Special Cost Price', index=True)
