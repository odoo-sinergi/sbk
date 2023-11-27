# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleReport(models.Model):
    _inherit='ir.actions.act_window'
    _description="Default view mode for sale analysis"

    @api.model
    def _get_default_value(self):
        return "pivot,graph"
    view_mode = fields.Char('View Mode', required=True,default=lambda self: self._get_default_value())