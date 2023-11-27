from odoo import api, fields, models


class FleetCapacity(models.Model):
    _name = 'fleet_capacity.fleet_capacity'
    _description = 'Fleet Capacity'

    name = fields.Char(string='Name')
    vehicle = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle')
    carton_type = fields.Many2one(
        comodel_name='fleet_capacity.carton_type', string='Carton Type')
    capacity = fields.Float(
        string='Capacity', compute='_compute_capacity', store=True)

    @api.depends('vehicle', 'carton_type')
    def _compute_capacity(self):
        for rec in self:
            container_volume = rec.vehicle.container_height * \
                rec.vehicle.container_width * rec.vehicle.container_depth
            carton_volume = rec.carton_type.height * \
                rec.carton_type.width * rec.carton_type.depth

            if carton_volume != 0:
                rec.capacity = float(container_volume / carton_volume)
            else:
                rec.capacity = container_volume
