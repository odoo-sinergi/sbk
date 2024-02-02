from odoo import models, fields, api, exceptions, _
from . import terbilang

class AccountMove(models.Model):
    _inherit = "account.move"
    _template = 'form_standard_odoo.standard_sales_invoice_document'

    source_picking = fields.Char("Picking Source", compute="_compute_source_picking")

    def terbilang_idr(self):
        return terbilang.terbilang(self.amount_total, 'idr', 'id')

    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(self._template)
        docargs = {
            'terbilang_idr': self.terbilang_idr,
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render(self._template, docargs)
    
    @api.depends('invoice_origin')
    def _compute_source_picking(self):
        for am in self:
            so_obj = self.env['sale.order'].search([('name', '=', am.invoice_origin)])
            picking_name = False
            if so_obj:
                picking_obj = self.env['stock.picking'].search([('origin','=',so_obj.name)])
            if picking_obj:
                picking_name = picking_obj.name
            am.source_picking = picking_name