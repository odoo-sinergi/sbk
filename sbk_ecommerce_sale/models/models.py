import logging
from odoo.exceptions import UserError
from odoo import models, tools, fields, api, _
from odoo.tools import float_is_zero, float_compare, pycompat

_logger = logging.getLogger(__name__)


class ShippingMethod(models.Model):
    _name = "sale.shippingmethod"
    _description = "Shipping Method"
    _order = "name"
    name = fields.Char('Shipping Method', required=True, translate=True)
    # is_dropshipping = fields.Boolean(string='Is Drop-Shipping?', default=True,
    #                                  help="Check this box if this is drop shipping method.")
    # active = fields.Boolean(
    #     default=True, help="If the active field is set to false, it will allow you to hide the Sales Team without removing it.")


class Invoice(models.Model):
    _inherit = 'account.invoice'
    shipping_method = fields.Many2one(
        'sale.shippingmethod', string='Shipping Method')
    is_ecommerce_sale = fields.Boolean(string='Is eCommerce Sale?', default=False,
                        help="Check this box if this is ecommerce sale.")
    e_commerce_invoice_no = fields.Char(index=True)
    ecommerce_cus_name = fields.Char(string='eCommerce Customer Name', index=True)
    is_dropshipping = fields.Boolean(string='Is Drop-Ship?', default=False,
                        help="Check this box if this is drop-ship.")
    so_po_number = fields.Char(index=True)
    freight = fields.Float(string="Freight")

    # @api.onchange('is_ecommerce_sale')
    # def is_ecommerce_sale_onchage_(self):
    #     self.e_commerce_invoice_no = ''

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax + self.freight
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self._get_aml_for_amount_residual():
            residual_company_signed += line.amount_residual
            if line.currency_id == self.currency_id:
                residual += line.amount_residual_currency if line.currency_id else line.amount_residual
            else:
                if line.currency_id:
                    residual += line.currency_id.with_context(date=line.date).compute(line.amount_residual_currency, self.currency_id)
                else:
                    residual += line.company_id.currency_id.with_context(date=line.date).compute(line.amount_residual, self.currency_id)
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual + self.freight)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    is_ecommerce_sale = fields.Boolean(string='Is eCommerce Sale?', default=False,
                                       help="Check this box if this is ecommerce sale.")
    is_dropshipping = fields.Boolean(string='Is Drop-Shipping?', default=False,
                                     help="Check this box if this is drop shipping method.")
    ecommerce_invoice_number = fields.Char(index=True)
    ecommerce_cus_name = fields.Char(index=True, string='eCommerce Customer Name')
    shipping_method = fields.Many2one(
        'sale.shippingmethod', string='Shipping Method')
    so_po_number = fields.Char(index=True)
    estimated_freight = fields.Float(string="Estimated Freight")
    web_so = fields.Boolean("E-commerace SO ")
    @api.onchange('is_ecommerce_sale')
    def is_ecommerce_sale_onchage_(self):
        self.ecommerce_invoice_number = ''
        self.ecommerce_cus_name = ''

    @api.onchange('estimated_freight','packaging_price')
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            amount_untaxed = amount_untaxed
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            print(self.packaging_price,"Pafa")
            order.update({
                'amount_untaxed': self.parse_num(amount_untaxed),
                'amount_tax': self.parse_num(amount_tax),
                'amount_total': self.parse_num(amount_untaxed + amount_tax + self.estimated_freight + self.packaging_price),
            })

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        company_id = self.company_id.id
        journal_id = (self.env['account.invoice'].with_context(company_id=company_id or self.env.user.company_id.id)
            .default_get(['journal_id'])['journal_id'])
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'e_commerce_invoice_no': self.ecommerce_invoice_number,
            'ecommerce_cus_name': self.ecommerce_cus_name,
            'is_ecommerce_sale': self.is_ecommerce_sale,
            'is_dropshipping': self.is_dropshipping,
            'shipping_method': self.shipping_method.id,
            'so_po_number': self.so_po_number,
            'freight': self.estimated_freight,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': company_id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        # _logger.warning("KNK INVOICE : %s",invoice_vals)
        return invoice_vals

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()

                    invoice = inv_obj.create(inv_data)
                    print(invoice, "INVOICE ds")
                    if order.packaging_price > 0:
                        invoice.amount_total = invoice.amount_total - order.packaging_price
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})

        if not invoices:
            raise UserError(_('There is no invoiceable line.'))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes and cash rounding. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice._onchange_cash_rounding()
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': references[invoice]},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
# # Over-riding stock.picking->validation_button to enable notification to SalesPerson
# # stock.picking.sale_id.user_id labelled SalesPerson
# class Picking(models.Model):
#     _inherit = 'stock.picking'
#     _description = 'Enabeling notifications on validation'

#     # Over-riding state field and added another state;
#     state = fields.Selection([
#     ('draft', 'Draft'),
#     ('waiting', 'Waiting Another Operation'),
#     ('confirmed', 'Waiting'),
#     ('assigned', 'Ready'),
#     ('pickedup', 'Pickedup'),
#     ('done', 'Done'),
#     ('cancel', 'Cancelled'),
# ], string='Status', compute='_compute_state',
#     copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
#     help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
#             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
#             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
#             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
#             " * Done: has been processed, can't be modified or cancelled anymore.\n"
#             " * Cancelled: has been cancelled, can't be confirmed anymore.")

#     show_pickedup = fields.Boolean(
#     compute='_compute_show_pickedup',
#     help='Technical field used to compute whether the validate should be shown.')


#     @api.multi
#     def button_validate(self):
#         self.ensure_one()
#         if not self.move_lines and not self.move_line_ids:
#             raise UserError(('Please add some lines to move'))
#         # If no lots when needed, raise error
#         picking_type = self.picking_type_id
#         precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#         no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
#         no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
#         if no_reserved_quantities and no_quantities_done:
#             raise UserError(('You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

#         if picking_type.use_create_lots or picking_type.use_existing_lots:
#             lines_to_check = self.move_line_ids
#             if not no_quantities_done:
#                 lines_to_check = lines_to_check.filtered(
#                     lambda line: float_compare(line.qty_done, 0,
#                                                precision_rounding=line.product_uom_id.rounding)
#                 )

#             for line in lines_to_check:
#                 product = line.product_id
#                 if product and product.tracking != 'none':
#                     if not line.lot_name and not line.lot_id:
#                         raise UserError(('You need to supply a lot/serial number for %s.') % product.display_name)

#         if no_quantities_done:
#             view = self.env.ref('stock.view_immediate_transfer')
#             wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
#             self.notlify(self.name)
#             return {
#                 'name': ('Immediate Transfer?'),
#                 'type': 'ir.actions.act_window',
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'stock.immediate.transfer',
#                 'views': [(view.id, 'form')],
#                 'view_id': view.id,
#                 'target': 'new',
#                 'res_id': wiz.id,
#                 'context': self.env.context,
#             }

#         if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
#             view = self.env.ref('stock.view_overprocessed_transfer')
#             wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
#             self.notlify(self.name)
#             return {
#                 'type': 'ir.actions.act_window',
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'stock.overprocessed.transfer',
#                 'views': [(view.id, 'form')],
#                 'view_id': view.id,
#                 'target': 'new',
#                 'res_id': wiz.id,
#                 'context': self.env.context,
#             }

#         # Check backorder should check for other barcodes
#         if self._check_backorder():
#             return self.action_generate_backorder_wizard()
#         self.action_done()

#         return

#     def notlify(self, order_no):
#         try:
#             self.env['mail.message'].create({'message_type':"notification",
#             "subtype": self.env.ref("mail.mt_comment").id,
#             'body': "The order number {order_no} have been picked and is ready for shipping",
#             'subject': "Stock Picking Notice",
#             'needaction_partner_ids': [(4,self.sale_id.user_id.partner_id.id)],
#             'model': self._name,
#             'res_id': self.id,
#             })
#         except ValueError:
#             raise UserError('Sale Person isn\'t selected or have been removed from record. ')


# # Button Visibility
#     @api.multi
#     @api.depends('state', 'is_locked')
#     def _compute_show_validate(self):
#         for picking in self:
#             if self._context.get('planned_picking') and picking.state == 'draft':
#                 picking.show_validate = False
#             elif picking.state not in ('draft', 'waiting', 'confirmed', 'pickedup') or not picking.is_locked:
#                 picking.show_validate = False
#             # elif picking.show_pickedup == True:
#             #     picking.show_validate = False
#             else:
#                 picking.show_validate = True

# # Pickeup button visibility
#     @api.multi
#     @api.depends('state', 'is_locked')
#     def _compute_show_pickedup(self):
#         for picking in self:
#             if self._context.get('planned_picking') and picking.state == 'draft':
#                 picking.show_pickedup = False
#             elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned' ) or not picking.is_locked:
#                 picking.show_pickedup = False

#             else:
#                 picking.show_pickedup = True

#     @api.multi
#     def button_pickedup(self):
#         try:
#             # Comprised order by directly making a move in stocks.
#             self.notlify(self.name)
#             for picking in self:
#                 picking.update({
#                     'state':'pickedup'
#                 })

#         except ValueError:
#             raise UserError('Something went wrong, please try again')
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):

        res= super(SaleAdvancePaymentInv, self).create_invoices()

        active = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].search([('id','=',active)])
        company_id = sale_order.company_id.id
        account_id = sale_order.partner_id.property_account_position_id
        journal_id = (self.env['account.invoice'].with_context(company_id=company_id or self.env.user.company_id.id)
            .default_get(['journal_id'])['journal_id'])
        print(account_id,"accp")
        if sale_order.packaging_price >0 :
            invoice = self.env['account.invoice']
            invoice_vals = {
                'name': sale_order.client_order_ref or '',
                'origin': sale_order.name,
                'e_commerce_invoice_no': sale_order.ecommerce_invoice_number,
                'ecommerce_cus_name': sale_order.ecommerce_cus_name,
                'is_ecommerce_sale': sale_order.is_ecommerce_sale,
                'is_dropshipping': sale_order.is_dropshipping,
                'shipping_method': sale_order.shipping_method.id,
                'so_po_number': sale_order.so_po_number,
                'freight': 0.0,
                'type': 'out_invoice',
                'account_id': sale_order.partner_invoice_id.property_account_receivable_id.id,
                'partner_id': sale_order.partner_invoice_id.id,
                'partner_shipping_id': sale_order.partner_shipping_id.id,
                'journal_id': journal_id,
                'currency_id': sale_order.pricelist_id.currency_id.id,
                'comment': sale_order.note,
                'payment_term_id': sale_order.payment_term_id.id,
                'fiscal_position_id': sale_order.fiscal_position_id.id or sale_order.partner_invoice_id.property_account_position_id.id,
                'company_id': company_id,
                'user_id': sale_order.user_id and sale_order.user_id.id,
                'team_id': sale_order.team_id.id
            }
            creat_invoice = invoice.create(invoice_vals)
            line= creat_invoice.invoice_line_ids.create({
                    'invoice_id' : creat_invoice.id,
                    'product_id' :False,
                    'name' : ' Packaging Price',
                       'account_id' :1,
                    'quantity' : 1,
                    'price_unit' :sale_order.packaging_price
                })

        return  res
