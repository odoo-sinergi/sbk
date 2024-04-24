from odoo import models, fields

class Company(models.Model):
    _inherit = 'res.company'

    company_details2 = fields.Html(string='Company Details', help="Header text displayed at the top of all reports.")
