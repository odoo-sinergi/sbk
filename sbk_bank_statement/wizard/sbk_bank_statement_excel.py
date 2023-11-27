import base64
import io

from odoo import api, fields, models, time, _
from odoo.exceptions import Warning, UserError
from datetime import datetime
import pytz

import logging
_logger = logging.getLogger(__name__)


class SBSExStatement(models.AbstractModel):
    _name = 'report.sbk_bank_statement.sb_statement'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            obj.model = self.env.context.get('active_model')
            docs = self.env[obj.model].browse(self.env.context.get('active_id'))

            comp = self.env.user.company_id.name
            sheet_name = "SBS"
            sheet = workbook.add_worksheet(sheet_name)
            format4 = workbook.add_format({'font_size': 16, 'align': 'center', 'bold': True, 'text_wrap': True})
            formate5 = workbook.add_format({'font_size': 12, 'align': 'left'})
            formate6 = workbook.add_format({'font_size': 12, 'align': 'right', 'valign': 'vcenter', 'bold': True })
            formate7 = workbook.add_format()
            formate8 = workbook.add_format({'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'bold': True })
            formate8.set_border(1)

            formate7.set_font_name('Quantity')
            formate6.set_border(1)
            formate5.set_bg_color('blue')
            formate5.set_font_color('white')
            formate5.set_border(1)
            sheet.merge_range('A1:H1', 'BANK STATEMENT', format4)
            sheet.merge_range('A2:G2', 'Starting Balance: ', formate6)
            sheet.write('H2:H2', docs.s_balance, formate6)

            sheet.set_column('A3:A3', 12)
            sheet.write('A3', "Date", formate8)
            sheet.set_column('B3:B3', 12)
            sheet.write('B3:B3', "Label", formate8)
            sheet.set_column('C3:C3', 15)
            sheet.write('C3', "Partner", formate8)
            sheet.set_column('D3:D3', 12)
            sheet.write('D3', "Reference", formate8)
            sheet.set_column('E3:E3', 20)
            sheet.write('E3', "Code/Name", formate8)
            sheet.set_column('F3:F3', 18)
            sheet.write('F3', "Debit", formate8)
            sheet.set_column('G3:G3', 18)
            sheet.write('G3:G3', "Credit", formate8)
            sheet.set_column('H3:H3', 20)
            sheet.write('H3:H3', "Amount", formate8)
            

            row_format = workbook.add_format({'font_size': 9, 'text_wrap': True, 'align': 'center', })
            row_format.set_border(1)
            row = 3
            for line in docs.statement_lines:
                sheet.set_row(row, 34)
                sheet.write(row, 0, line.date, row_format)
                sheet.write(row, 1, line.label, row_format)
                sheet.write(row, 2, line.partner, row_format)
                sheet.write(row, 3, line.reference, row_format)
                sheet.write(row, 4, line.code_name, row_format)
                sheet.write(row, 5, line.debit, row_format)
                sheet.write(row, 6, line.credit, row_format)
                sheet.write(row, 7, line.amount, row_format)
                row = row + 1
            str_a = 'A' + str(row+1) + ':G' + str(row+1)
            str_b = 'H' + str(row+1) +':H' + str(row+1)
            sheet.merge_range(str_a, 'Ending Balance: ', formate6)
            sheet.write(str_b, docs.e_balance, formate6)