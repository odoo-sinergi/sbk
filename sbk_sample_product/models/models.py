import json
import logging
from odoo.exceptions import UserError
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    is_sample = fields.Boolean(string='Is Sample Product?', default=False,
                                       help="Check this box if this is sample product.")

    @api.onchange('is_sample')
    def _sample_product(self):
        _logger.warning("KNK : %s",self._get_display_price(self.product_id))
        if(self.is_sample == True):
            self.price_unit = 0
        else:
            self.price_unit = self._get_display_price(self.product_id)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'is_sample')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if(line.is_sample == True):
                price = 0
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'price_unit': price
            })