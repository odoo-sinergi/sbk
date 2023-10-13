# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    force_date = fields.Datetime(string="Force Date")


    def button_validate(self):
        # do actual processing
        res = super().button_validate()
        # overwrite date field where applicable
        if self.env.user.has_group('stock_force_date_app.group_stock_force_date'):
            for picking in self:
                if picking.force_date:        
                    for move in picking.move_ids_without_package:
                        sql_query="""Update stock_valuation_layer set create_date=%s where stock_move_id=%s
                            """
                        self.env.cr.execute(sql_query,(picking.force_date,move.id,))
                        # svl_obj=self.env['stock.valuation.layer'].search([('stock_move_id','=',move.id)])
                        # if svl_obj:
                        #     svl_obj.write({'create_date':self.force_date})
        return res
        