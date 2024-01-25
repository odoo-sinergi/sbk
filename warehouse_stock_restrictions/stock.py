# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        for rec in self:
            if rec.state == 'draft':
                return True

            user_locations = []
            for i in rec.env.user.stock_location_ids:
                user_locations.append(i.id)

            # user_locations = rec.env.user.stock_location_ids
            if rec.env.user.restrict_locations:
                message = _(
                    'Invalid Location. You cannot process this move since you do '
                    'not control the location "%s". '
                    'Please contact your Administrator.')

                if rec.location_id.id not in user_locations:
                    raise UserError(message % rec.location_id.name)
                elif rec.location_dest_id.id not in user_locations:
                    raise UserError(message % rec.location_dest_id.name)

class allow_warehouse(models.Model):
    _inherit = 'sale.order'

    
    @api.model
    def _sdt_default_warehouse_id(self):
        warehouse = False
        for wh in self:
            if wh.warehouse_id:
                warehouse = wh.warehouse_id
            else:
                warehouse = self.env.user._get_default_warehouse_id()
        return warehouse

    warehouse_loc_id = fields.Many2one(
        'stock.warehouse', string='Warehouse Location',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        check_company=True, default=_sdt_default_warehouse_id)

    @api.onchange('partner_id')
    def set_domain_for_warehouse(self):
        if self.warehouse_loc_id.id==False and self.warehouse_id.id==True:
            self.warehouse_loc_id = self.warehouse_id
        class_obj = self.env['res.users']
        loc_ids=[]
        for data in class_obj.env.user.default_picking_type_ids:
            loc_ids.append(data.warehouse_id.id)

        res = {}
        res['domain'] = {'warehouse_loc_id': [('id', 'in', loc_ids)]}
        return res

    @api.onchange('warehouse_id')
    def sdt_onchange_warehouse(self):
        if self.warehouse_id:
            self.warehouse_loc_id = self.warehouse_id


    @api.model
    def create(self, vals):
        vals['warehouse_loc_id'] = vals['warehouse_id'] or self.env.user._get_default_warehouse_id()
        result = super().create(vals)
        return result




