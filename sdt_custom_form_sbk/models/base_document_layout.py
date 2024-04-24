# -*- coding: utf-8 -*-

import markupsafe
from markupsafe import Markup
from odoo import api, models, fields, tools
from odoo.addons.base.models.ir_qweb_fields import nl2br

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'
    
    company_details2 = fields.Html(related='company_id.company_details2', readonly=False)