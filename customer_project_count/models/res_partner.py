# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """ Inherits partner and adds Projects information in the partner form """
    _inherit = 'res.partner'

    project_ids = fields.One2many(
        'project.project', 'partner_id', string='Projects')
    project_count = fields.Integer(
        compute='_compute_project_count', string='# Projects')

    def _compute_project_count(self):
        fetch_data = self.env['project.project'].read_group(
            [('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        result = dict((data['partner_id'][0], data['partner_id_count'])
                      for data in fetch_data)
        for partner in self:
            partner.project_count = result.get(partner.id, 0)
