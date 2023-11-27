from odoo import api, tools, fields, models, _
from odoo.exceptions import ValidationError
import logging
from odoo.tools import float_compare, pycompat
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    secondary_uom_id = fields.Many2one('product.uom', string="Secondary Unit of Measure")
    second_uom_name = fields.Char(related="secondary_uom_id.name", readonly=True)
    secondary_uom_qty = fields.Float(compute='_convert_secondary_uom_qty', string="On Hand in Secondary UoM")
    second_virtual_available = fields.Float(compute='_convert_secondary_uom_qty', string="'Forecast Qty-Secondary UoM'")
    # Join this to product.uom;
    custom_factor = fields.Float(string="Custom Factor", help='How much bigger or smaller this unit is compared to the reference Unit of Measure for this category: 1 * (reference unit) = ratio * (this unit)')

    @api.multi
    def _convert_secondary_uom_qty(self):
        for rec in self:
            second_uom_id = rec.secondary_uom_id
            if second_uom_id.category_id.id:
                if rec.uom_id.category_id.id != second_uom_id.category_id.id:
                    rec.secondary_uom_qty = 0
                    rec.second_virtual_available = 0
                else:
                    on_hand = rec.qty_available
                    virtual_available = rec.virtual_available
                    secondary_uom_qty = rec.uom_id._compute_quantity(qty=on_hand, to_unit=second_uom_id)
                    rec.secondary_uom_qty = secondary_uom_qty                    
                    second_virtual_available = rec.uom_id._compute_quantity(qty=virtual_available, to_unit=second_uom_id)
                    rec.second_virtual_available = second_virtual_available
                    
    @api.multi
    def dummy_btn(self):
        pass
    
    @api.constrains('uom_id', 'uom_po_id', 'secondary_uom_id')
    def _check_uom(self):
        res = super(ProductTemplate, self)._check_uom()
        if any(template.uom_id and template.uom_po_id and template.secondary_uom_id and template.uom_id.category_id != template.secondary_uom_id.category_id for template in self):
            raise ValidationError(_('The default Unit of Measure and the Secondary Unit of Measure must be in the same category.'))
        return res

# Extracting and tweaking factor if secondary factor exists;
class ProductUOM(models.Model):
    _inherit='product.uom'
    _description="tweaking product.uom's factor is secondary factor exsits, overriding"

    @api.multi
    def _compute_quantity(self, qty, to_unit, round=True, rounding_method='UP'):
        if not self:
            return qty
        self.ensure_one()
        if self.category_id.id != to_unit.category_id.id:
            if self._context.get('raise-exception', True):
                raise UserError(_('Conversion from Product UoM %s to Default UoM %s is not possible as they both belong to different Category!.') % (self.name, to_unit.name))
            else:
                return qty
        amount = qty / self.factor
        if to_unit:
            amount = amount * to_unit.factor
            if round:
                amount = tools.float_round(amount, precision_rounding=to_unit.rounding, rounding_method=rounding_method)
        
        return amount

    
    @api.multi
    def _compute_price(self, price, to_unit, newFactor = 0):
        self.ensure_one()
        if not self or not price or not to_unit or self == to_unit:
            return price
        if self.category_id.id != to_unit.category_id.id:
            return price
        amount = price * self.factor
        if newFactor > 0:
            amount = amount / newFactor
        elif to_unit:
            amount = amount / to_unit.factor       
        return amount


class ProductProduct(models.Model):
    _inherit='product.product'
    _description='product product'
    
    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                prices[product.id] += product.price_extra
            custom_factor = 0
            if  product.product_tmpl_id.custom_factor >= 0:
                custom_factor = product.product_tmpl_id.custom_factor
            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom, custom_factor)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)

        return prices