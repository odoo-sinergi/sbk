# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class StockQuant(models.Model):
	_inherit = 'stock.quant'

	
	def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
		""" Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param out: boolean to set on True when the move go to inventory adjustment location.
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
		self.ensure_one()
		if fields.Float.is_zero(qty, 0, precision_rounding=self.product_uom_id.rounding):
			name = _('Product Quantity Confirmed')
		else:
			name = _('Product Quantity Updated')
		
		force_date = self.accounting_date or fields.Date.today()

		return {
            'name': self.env.context.get('inventory_name') or name,
			'date':force_date,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'is_inventory': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': self.lot_id.id,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'owner_id': self.owner_id.id,
            })]
        }
	
	# def _apply_inventory(self):
	# 	move_vals = []
	# 	force_date = fields.Date.today()
	# 	if not self.user_has_groups('stock.group_stock_manager'):
	# 		raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
	# 	for quant in self:
	# 		# Create and validate a move so that the quant matches its `inventory_quantity`.
	# 		if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
	# 			move_vals.append(
	# 				quant._get_inventory_move_values(quant.inventory_diff_quantity,
	# 												quant.product_id.with_company(quant.company_id).property_stock_inventory,
	# 												quant.location_id))
	# 		else:
	# 			move_vals.append(
	# 				quant._get_inventory_move_values(-quant.inventory_diff_quantity,
	# 												quant.location_id,
	# 												quant.product_id.with_company(quant.company_id).property_stock_inventory,
	# 												out=True))
	# 		if self.env.user.has_group('stock_force_date_app.group_stock_force_date'):
	# 			force_date = quant.accounting_date or force_date
	# 		for move in move_vals:
	# 			move['date'] = force_date
	# 			for move_line in move['move_line_ids']:
	# 				move_line[2]['date'] = force_date

	# 	moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
	# 	moves.with_context(accounting_date=quant.accounting_date)._action_done()
	# 	for quant in self:
	# 		force_date = quant.accounting_date or fields.Date.today() if self.env.user.has_group('stock_force_date_app.group_stock_force_date') else fields.Date.today()
	# 		for move in moves:
	# 			if move.date != force_date:
	# 				# for move_line in move.move_line_ids:
	# 				# 	move_line.update({'date':force_date})
	# 				for valuation in move.stock_valuation_layer_ids:
	# 					# valuation.update({'create_date':force_date})
	# 					sql_query="""update stock_valuation_layer set create_date=%s where id=%s
	# 						"""
	# 					self.env.cr.execute(sql_query,(force_date,valuation.id,))
	# 					# for am in valuation.account_move_id:
	# 					# 	am.update({'date':force_date})
	# 	self.location_id.write({'last_inventory_date': fields.Date.today()})
	# 	date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
	# 	for quant in self:
	# 		quant.inventory_date = date_by_location[quant.location_id]
	# 	self.write({'inventory_quantity': 0, 'user_id': False})
	# 	self.write({'inventory_diff_quantity': 0})


	def _apply_inventory(self):
		move_vals = []
		if not self.user_has_groups('stock.group_stock_manager'):
			raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
		for quant in self:
			# Create and validate a move so that the quant matches its `inventory_quantity`.
			move_vals = []
			if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
				move_vals.append(
					quant._get_inventory_move_values(quant.inventory_diff_quantity,
													quant.product_id.with_company(quant.company_id).property_stock_inventory,
													quant.location_id))
				moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
				moves.with_context(accounting_date=quant.accounting_date)._action_done()
			else:
				move_vals = []
				move_vals.append(
                    quant._get_inventory_move_values(-quant.inventory_diff_quantity,
													quant.location_id,
													quant.product_id.with_company(quant.company_id).property_stock_inventory,
													out=True))
				moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
				moves.with_context(accounting_date=quant.accounting_date)._action_done()
		has_forcedate_group = self.env.user.has_group('stock_force_date_app.group_stock_force_date')
		for quant in self:
			force_date = quant.accounting_date or fields.Date.today() if has_forcedate_group else fields.Date.today() 
			for move in moves:
				move.update({'date':force_date})
				for move_line in move.move_line_ids:
					move_line.update({'date':force_date})
				for valuation in move.stock_valuation_layer_ids:
					valuation.update({'create_date':force_date})
					sql_query="""update stock_valuation_layer set create_date=%s where id=%s
						"""
					self.env.cr.execute(sql_query,(force_date,valuation.id,))
					for am in valuation.account_move_id:
						am.update({'date':force_date})
		self.location_id.write({'last_inventory_date': fields.Date.today()})
		date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
		for quant in self:
			quant.inventory_date = date_by_location[quant.location_id]
		self.write({'inventory_quantity': 0, 'user_id': False})
		self.write({'inventory_diff_quantity': 0})