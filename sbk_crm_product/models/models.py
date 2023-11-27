from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductLine(models.Model):
    _name = 'sbk_crm_product.crm.product.line'

    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Ordered Qty',default=1.0)
    uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    enquiry_date = fields.Datetime(default=fields.Datetime.now, readonly=True)
    crm_id = fields.Many2one('crm.lead')

    @api.onchange('qty')
    def _onchage_enquiry_date(self):
        self.enquiry_date = fields.Datetime.now()
    @api.multi
    def write(self, vals):
        if 'qty' in vals:
            vals['enquiry_date'] = fields.Datetime.now()
        res = super(ProductLine, self).write(vals)
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.lst_price


class Lead(models.Model):
    _inherit = 'crm.lead'
    product_line_ids = fields.One2many('sbk_crm_product.crm.product.line', 'crm_id',string='Products For Quotation')

    @api.multi
    def action_create_quotation(self):
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        order_lines = []
        for line in self.product_line_ids:
            order_lines.append((0,0,{'product_id': line.product_id.id,
                'name': line.description,
                'product_uom_qty':line.qty,


            }))
        if self.partner_id:
            sale_id = sale_obj.create({
                'partner_id':self.partner_id.id,
                'team_id': self.team_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'source_id': self.source_id.id,
                'opportunity_id': self.id,
                'order_line':order_lines,
            })
        else:
            raise UserError('In order to create sale order, Customer field should not be empty !!!')
        return True



