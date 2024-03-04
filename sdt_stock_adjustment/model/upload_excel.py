# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from  odoo.exceptions import UserError,ValidationError
from xlrd import open_workbook

import base64
import tempfile
import logging
_logger = logging.getLogger(__name__)

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

class UploadExcel(models.TransientModel):
    _name = 'upload.excel'

    receipt_id = fields.Integer('Receipt Id',default=False,readonly=True)
    file = fields.Binary('Excel File ')

    @api.model
    def default_get(self, fields):
        receipt_id = self._context.get('receipt_ids')
        rec = super(UploadExcel, self).default_get(fields)
        if receipt_id:
            rec.update({'receipt_id': receipt_id[0]})

        return rec

    def create_upload(self):
        file_path = self.file
        wb = open_workbook(file_contents=base64.decodestring(self.file))
        sheet = wb.sheets()[0]
        data = []
        i = 1
        detail_id=self.receipt_id
        line_env = self.env['sdt.stock.adjustment.details'].search([('detail_id','=',detail_id)])
        if line_env:
            line_env.unlink()
        line_env = self.env['sdt.stock.adjustment.details']
        for k in range(1, sheet.nrows):
            product_id=int(sheet.cell_value(i,0))
            lot_id=sheet.cell_value(i,1)
            quantity=sheet.cell_value(i,2)
            product_obj=self.env['product.product'].search([('id','=',product_id)])
            if not product_obj:
                raise UserError("Product id " + str(product_id) + " not found..!")
            if product_obj.product_tmpl_id.type!='product':
                raise UserError("Product id " + str(product_id) + " is not stockable..!")
            if product_obj.product_tmpl_id.standard_price ==0:
                raise UserError("Product id " + str(product_id) + " cost is 0..!")
            product_uom_id = product_obj.product_tmpl_id.uom_id.id
            # if lot_name:
            #     lot_find = self.env['stock.production.lot'].search(['&', ('name', '=', lot_name), ('product_id', '=', product_id)], limit=1)
            #     if not lot_find:
            #         lot_obj = self.env['stock.production.lot'].create({'name': lot_name, 'product_id': product_id})
            #         lot_id = lot_obj.id
            #     else:
            #         lot_id = lot_find.id

            line_env.create({
                'detail_id': detail_id,
                'product_id': product_id,
                'product_uom_id': product_uom_id,
                'lot_id': lot_id,
                'quantity': quantity})
            i = i + 1
