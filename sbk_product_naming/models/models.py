import json
import logging
from odoo.exceptions import UserError
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    printout_name = fields.Char(string='Original Name', index=True, stored=True)


class PurchaseOrderLineSBK(models.Model):
    _inherit = 'purchase.order.line'

    original_name = fields.Char(string='Original Name', related='product_id.printout_name')