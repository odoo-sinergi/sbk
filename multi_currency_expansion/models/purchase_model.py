from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.base_currency_price_tax', 
            'order_line.base_currency_price_total', 
            'order_line.base_currency_price_subtotal')
    def _amount_all_with_base_currency(self):
        base_currency = self.env.user.company_id.currency_id
        for order in self:
            base_currency_amount_untaxed = base_currency_amount_tax = 0.0
            for line in order.order_line:
                base_currency_amount_untaxed += line.base_currency_price_subtotal
                base_currency_amount_tax += line.base_currency_price_tax
            order.update({
                'base_currency_amount_untaxed': base_currency.round(base_currency_amount_untaxed),
                'base_currency_amount_tax': base_currency.round(base_currency_amount_tax),
                'base_currency_amount_total': base_currency_amount_untaxed + base_currency_amount_tax,
            })
    
    def _get_base_currency_id(self):
        return self.env.user.company_id.currency_id.id
            
    base_currency_amount_untaxed = fields.Monetary(string='Untaxed Amount (Base Currency)', 
            store=True, readonly=True, compute='_amount_all_with_base_currency')
    base_currency_amount_tax = fields.Monetary(string='Taxes (Base Currency)', 
            store=True, readonly=True, compute='_amount_all_with_base_currency')
    base_currency_amount_total = fields.Monetary(string='Total (Base Currency)', 
            store=True, readonly=True, compute='_amount_all_with_base_currency')

    base_currency_id = fields.Many2one('res.currency', 'Base Currency', readonly=True, \
        compute='_get_base_currency_id')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('price_tax', 'price_total', 'price_subtotal', 'currency_id')
    def _compute_amount_with_base_currency(self):
        base_currency = self.env.user.company_id.currency_id
        for line in self:
            base_currency_price_tax = self.env['res.currency']._compute(line.currency_id, base_currency,line.price_tax)
            base_currency_price_total = self.env['res.currency']._compute(line.currency_id, base_currency, line.price_total)
            base_currency_price_subtotal = self.env['res.currency']._compute(line.currency_id, base_currency, line.price_subtotal)
            line.update({
                'base_currency_price_tax': base_currency_price_tax,
                'base_currency_price_total': base_currency_price_total,
                'base_currency_price_subtotal': base_currency_price_subtotal
            })

    base_currency_price_tax = fields.Float(compute='_compute_amount_with_base_currency', string='Tax (Base Currency)', store=True)
    base_currency_price_total = fields.Monetary(compute='_compute_amount_with_base_currency', string='Total (Base Currency)')
    base_currency_price_subtotal = fields.Monetary(compute='_compute_amount_with_base_currency', string='Subtotal (Base Currency)', store=True)

