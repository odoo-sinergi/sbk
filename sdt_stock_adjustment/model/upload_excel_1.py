# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from  odoo.exceptions import UserError,ValidationError
import importlib
import subprocess
try:
    import openpyxl
except ImportError:
    print("Modul 'openpyxl' tidak ditemukan. Menginstal...")
    subprocess.run(['pip3', 'install', 'openpyxl'])
    try:
        import openpyxl
    except ImportError:
        openpyxl = None
import base64
from io import BytesIO
import logging
_logger = logging.getLogger(__name__)


class UploadExcel(models.TransientModel):
    _name = 'upload.excel'

    receipt_id = fields.Integer('Receipt Id',default=False,readonly=True)
    file = fields.Binary('Excel File')

    @api.model
    def default_get(self, fields):
        receipt_id = self._context.get('receipt_ids')
        rec = super(UploadExcel, self).default_get(fields)
        if receipt_id:
            rec.update({'receipt_id': receipt_id[0]})

        return rec

    def create_upload(self):
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)), read_only=True)
        sheet = wb.active
        data = []
        i = 1
        j = 1
        name = ''
        adjustment_id=self.receipt_id
        line_env = self.env['sdt.stock.adjustment.details'].search([('adjustment_id','=',adjustment_id)])
        if line_env:
            line_env.unlink()
        line_env = self.env['sdt.stock.adjustment.details']
        for record in sheet.iter_rows(min_row=2, max_row=sheet._max_row-1, min_col=None, max_col=None, values_only=True):
            z = i % 300
            if z == 0:
                line = self.env['sdt.stock.adjustment.details'].search(
                    [('adjustment_id', '=', adjustment_id)], limit=1)
                name = line.adjustment_id.name +' '+ str(j)
                head = {
                    'name': name,
                    'location_id': line.adjustment_id.location_id.id
                }
                head_env = self.env['sdt.stock.adjustment'].create(head)
                j = j + 1

            # _logger.info('CHECK: product_id excel %s',record[0])
            if not record[0]:
                continue
            product_id=int(record[0])
            _logger.info('CHECK: product_id %s',product_id)
            lot_name=record[1] or ''
            quantity=record[2]
            product_obj=self.env['product.product'].search([('id','=',product_id)])
            if not product_obj:
                raise UserError("Product id " + str(product_id) + " not found..!")
            if product_obj.product_tmpl_id.type!='product':
                raise UserError("Product id " + str(product_id) + " is not stockable..!")
            if product_obj.product_tmpl_id.standard_price ==0:
                raise UserError("Product id " + str(product_id) + " [%s] cost is 0..!" %(product_obj.display_name))
            product_uom_id = product_obj.product_tmpl_id.uom_id.id
            
            if name:
                line = self.env['sdt.stock.adjustment'].search([('name', '=', name)])
                detail = (0, 0, {
                    'adjustment_id': adjustment_id,
                    'product_id': product_id,
                    'product_uom_id': product_uom_id,
                    'lot_name': lot_name,
                    'quantity': quantity
                })
                data.append(detail)
                line.write({'detail_ids': data})
                data = []
                i = i + 1
            else:    
                line_env.create({
                    'adjustment_id': adjustment_id,
                    'product_id': product_id,
                    'product_uom_id': product_uom_id,
                    'lot_name': lot_name,
                    'quantity': quantity})
                i = i + 1
