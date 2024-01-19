# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from lxml import etree

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PriceRule(models.Model):
    _inherit = "delivery.price.rule"


    variable = fields.Selection([
        ('weight', 'Weight'), 
        ('volume', 'Volume'), 
        ('wv', 'Weight * Volume'), 
        ('price', 'Price'), 
        ('quantity', 'Quantity'),
        ('distance', 'Distance'),
        ])