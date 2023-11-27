# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class change_paper_format_viipc(models.Model):
#     _name = 'change_paper_format_viipc.change_paper_format_viipc'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100