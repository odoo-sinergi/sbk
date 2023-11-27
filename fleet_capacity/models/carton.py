from odoo import api, fields, models


class Carton(models.Model):
    _name = 'fleet_capacity.carton_type'
    _description = 'Carton Type'

    name = fields.Char(string='Name')
    height = fields.Float('Height')
    width = fields.Float('Width')
    depth = fields.Float('Depth')
