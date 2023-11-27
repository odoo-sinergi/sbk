import json
import logging

from datetime import datetime, timedelta, date
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)

class Inventory(models.Model):
    _inherit = "stock.inventory"

    user_id = fields.Many2one('res.users',
        'Performed By',
        default=lambda self: self.env.user,
        readonly=True,
        help="The user that create this Inventory Adjustment transaction")