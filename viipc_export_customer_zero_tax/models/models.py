from odoo import models, fields, api
import logging


class ResPartner(models.Model):
	""" inherit res.partner. """

	_inherit = 'res.partner'

	is_export_customer = fields.Boolean(string='Is an Export Customer', default=False,
							   help="Check this box if this contact is a export customer.")


	def set_is_export_customer(self):
		""" Saving the values to ir.values """

		irValues = self.env['ir.values']
		irValues.set_default('res.partner', 'is_export_customer', self.is_export_customer)

class SaleOrder(models.Model):
	"""inherit sale order."""
	_inherit = "sale.order"

	@api.onchange('partner_id')
	def _changed_customer(self):
		for line in self.order_line:
			line._compute_tax_id()


class SaleOrderLine(models.Model):
	"""inherit sale order."""
	_inherit = "sale.order.line"

	@api.onchange('order_partner_id')
	def _changed_customer(self):
		for line in self:
			line.tax_id = None if line.order_partner_id.is_export_customer else line.tax_id

	@api.multi
	def _compute_tax_id(self):

		for line in self:
			fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
			# If company_id is set, always filter taxes by the company
			taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
			line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
			line.tax_id = None if line.order_partner_id.is_export_customer else line.tax_id
