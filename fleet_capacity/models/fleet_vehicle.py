from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    container_height = fields.Float('Container Height')
    container_width = fields.Float('Container Width')
    container_depth = fields.Float('Container Depth')
