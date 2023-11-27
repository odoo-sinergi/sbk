import json
import logging

from datetime import datetime, timedelta, date
from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)

class Lead(models.Model):
    _inherit = "crm.lead"

    actual_create_date = fields.Datetime('Actual Creation Date', default=fields.Datetime.now)

