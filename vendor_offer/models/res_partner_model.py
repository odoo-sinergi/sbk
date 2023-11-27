from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    purchase_offers = fields.One2many(
            'product.supplierinfo',
            'name',
            'Purchase Offers',
            )
