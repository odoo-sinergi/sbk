# -*- coding: utf-8 -*-

import markupsafe
from markupsafe import Markup
from odoo import api, models, fields, tools
from odoo.addons.base.models.ir_qweb_fields import nl2br

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    @api.model
    def _default_company_details2(self):
        company = self.env.company
        address_format, company_data = company.partner_id._prepare_display_address()
        address_format = self._clean_address_format(address_format, company_data)
        # company_name may *still* be missing from prepared address in case commercial_company_name is falsy
        if 'company_name' not in address_format:
            address_format = '%(company_name)s\n' + address_format
            company_data['company_name'] = company_data['company_name'] or company.name
        return Markup(nl2br(address_format)) % company_data
    
    company_details2 = fields.Html(related='company_id.company_details', readonly=False, default=_default_company_details2)