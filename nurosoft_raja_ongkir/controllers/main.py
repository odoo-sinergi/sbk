from odoo import http, tools, _
from odoo.http import Controller, request, route
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import ValidationError, MissingError, AccessError
from odoo.fields import Command
from odoo.addons.payment.controllers.portal import PaymentPortal
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

class CustomerPortalInherit(CustomerPortal):

    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name","raja_ongkir_city", "raja_ongkir_city_id", "raja_ongkir_subdistrict_id"]
    
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post:
            if not post.get('raja_ongkir_city', False):
                post.pop('city')
            else:
                carrier = request.env['delivery.carrier'].sudo().search([('delivery_type','=','raja_ongkir')],limit=1)
                if carrier:
                    if carrier.raja_ongkir_destination_type == 'city':
                        city_id = request.env['raja.ongkir.city'].sudo().search([('city_id','=',post['raja_ongkir_city'])])
                        post['raja_ongkir_city_id'] = city_id.id or False
                    else:
                        subdistrict_id = request.env['raja.ongkir.subdistrict'].sudo().search([('subdistrict_id','=',post['raja_ongkir_city'])])
                        post['raja_ongkir_subdistrict_id'] = subdistrict_id.id or False
                    post.pop('raja_ongkir_city')

            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:        

                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'country_id': int(values.pop('country_id', 0))})
                values.update({'zip': values.pop('zipcode', '')})
                if values.get('state_id') == '':
                    values.update({'state_id': False})
                else:
                    values.update({'state_id': int(values.pop('state_id', 0))})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        carrier = request.env['delivery.carrier'].sudo().search([('delivery_type','=','raja_ongkir')],limit=1)
        raja_ongkir_city = False
        if carrier:          
            
            if partner and partner.id > 0:
                if carrier.raja_ongkir_destination_type == 'city':
                    raja_ongkir_city = partner.raja_ongkir_city_id.id if partner.raja_ongkir_city_id else False               
                else:
                    raja_ongkir_city = partner.raja_ongkir_subdistrict_id.id if partner.raja_ongkir_subdistrict_id else False

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
            'raja_ongkir_city': raja_ongkir_city,
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

class WebsiteSaleInherit(WebsiteSale):

    def values_preprocess(self, values):
        if not values.get('raja_ongkir_city'):
            values['city'] = False
        else:
            carrier = request.env['delivery.carrier'].sudo().search([('delivery_type','=','raja_ongkir')],limit=1)
            if carrier:
                if carrier.raja_ongkir_destination_type == 'city':
                    city_id = request.env['raja.ongkir.city'].sudo().search([('city_id','=',values['raja_ongkir_city'])])
                    values['raja_ongkir_city_id'] = city_id.id or False
                else:
                    subdistrict_id = request.env['raja.ongkir.subdistrict'].sudo().search([('subdistrict_id','=',values['raja_ongkir_city'])])
                    values['raja_ongkir_subdistrict_id'] = subdistrict_id.id or False
                values.pop('raja_ongkir_city')
        return super(WebsiteSaleInherit, self).values_preprocess(values)

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()
        temp_raja_ongkir_city = kw.get('raja_ongkir_city',False)
        temp_city = kw.get('city',False)

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            
            post['raja_ongkir_city_id'] = pre_values.get('raja_ongkir_city_id', False)
            post['raja_ongkir_subdistrict_id'] = pre_values.get('raja_ongkir_subdistrict_id', False)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)

                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    # order.onchange_partner_id()
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/checkout')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        
        carrier = request.env['delivery.carrier'].sudo().search([('delivery_type','=','raja_ongkir')],limit=1)
        raja_ongkir_city = False
        if carrier:
            partner_data = Partner.browse(partner_id)
            if partner_data and partner_data.id > 0:
                if carrier.raja_ongkir_destination_type == 'city':
                    raja_ongkir_city = partner_data.raja_ongkir_city_id.id if partner_data.raja_ongkir_city_id else False               
                else:
                    raja_ongkir_city = partner_data.raja_ongkir_subdistrict_id.id if partner_data.raja_ongkir_subdistrict_id else False
            else:
                if temp_raja_ongkir_city:
                    raja_ongkir_city = temp_raja_ongkir_city
                    values['city'] = temp_city
                    
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'raja_ongkir_city': raja_ongkir_city,
        }
        return request.render("website_sale.address", render_values)

class WebsiteSaleDelivery(WebsiteSaleDelivery):

    @http.route(['/shop/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id, post=post)
        return self._update_website_sale_delivery_return(order, **post)

    @http.route(['/shop/current_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_current_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        currency = order.currency_id
        if order and order.delivery_type == 'raja_ongkir':
            return self._update_website_sale_delivery_return(order, **post)
        else:
            return {'carrier_id': carrier_id}

    def _update_website_sale_delivery(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id, post=post)
        return self._update_website_sale_delivery_return(order, **post)

    @http.route(['/shop/get_carrier_type'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_carrier_type(self, **post):
        results = {}
        carrier_id = int(post['carrier_id'])
        carrier = request.env['delivery.carrier'].sudo().search([('id','=',carrier_id)],limit=1)
        
        order = request.website.sale_get_order()

        if carrier:
            results.update({'delivery_type': carrier.delivery_type, 'city': order.partner_shipping_id.city})
        return results

    @http.route(['/shop/get_carrier_list'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_carrier_list(self, **post):
        results = []
        domain = [('website_published','=',True)]
        fields = ['code','name']
        carriers = request.env['raja.ongkir.carrier'].sudo().search_read(domain=domain,fields=fields)
        if carriers:
            results = carriers
        return results

    @http.route(['/shop/get_city_list'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_city_list(self, **post):
        results = []
        name = post['name']
        carrier_id = post['carrier_id']

        carrier = request.env['delivery.carrier'].sudo().search([('id','=',carrier_id)],limit=1)

        if not carrier:
            carrier = request.env['delivery.carrier'].sudo().search([('delivery_type','=','raja_ongkir')],limit=1)

        if carrier.raja_ongkir_destination_type == 'city':
            domain = ['|',('name','ilike',name),('province','ilike',name)]
            fields = ['city_id','name','province', 'type']
            cities = request.env['raja.ongkir.city'].sudo().search_read(domain=domain,fields=fields)
            if cities:
                results.append({
                    'type': 'city',
                    'data': cities
                })
        else:
            domain = ['|','|',('name','ilike',name),('city','ilike',name),('province','ilike',name)]
            fields = ['subdistrict_id','name','city','province', 'city_type']
            subdistricts = request.env['raja.ongkir.subdistrict'].sudo().search_read(domain=domain,fields=fields)
            if subdistricts:
                results.append({
                    'type': 'subdistrict',
                    'data': subdistricts
                })
        return results

    @http.route(['/shop/get_destination_type'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_destination_type(self, **post):
        results = ''
        carrier = request.env['delivery.carrier'].sudo().search([('delivery_type','=','raja_ongkir')],limit=1)
        if carrier:
            results = carrier.raja_ongkir_destination_type
        return results

    @http.route(['/shop/get_carrier_cost'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def get_carrier_cost(self, **post):
        results = {'norajaongkir': {}}
        
        order = request.website.sale_get_order()

        carrier_id = int(post['carrier_id'])
        carrier = request.env['delivery.carrier'].sudo().search([('id','=',carrier_id)],limit=1)
        if carrier:
            if carrier.delivery_type == 'raja_ongkir':
                results = carrier.raja_ongkir_check_cost(order,**post)
        return results

class PaymentPortal(PaymentPortal):
    
    @http.route('/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True)
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The sales order to pay, as a `sale.order` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError(_("The access token is invalid."))

        if order_sudo.state == "cancel":
            raise ValidationError(_("The order has been canceled."))

        if order_sudo.carrier_id.delivery_type=='raja_ongkir':
            kwargs['amount'] = order_sudo.amount_total

        kwargs.update({
            'reference_prefix': None,  # Allow the reference to be computed based on the order
            'partner_id': order_sudo.partner_id.id,
            'sale_order_id': order_id,  # Include the SO to allow Subscriptions to tokenize the tx
        })
        kwargs.pop('custom_create_values', None)  # Don't allow passing arbitrary create values
        if not kwargs.get('amount'):
            kwargs['amount'] = order_sudo.amount_total

        if tools.float_compare(kwargs['amount'], order_sudo.amount_total, precision_rounding=order_sudo.currency_id.rounding):
            raise ValidationError(_("The cart has been updated. Please refresh the page."))

        tx_sudo = self._create_transaction(
            custom_create_values={'sale_order_ids': [Command.set([order_id])]}, **kwargs,
        )

        # Store the new transaction into the transaction list and if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentPostProcessing.remove_transactions(last_tx)
        request.session['__website_sale_last_tx_id'] = tx_sudo.id

        self._validate_transaction_for_order(tx_sudo, order_id)

        return tx_sudo._get_processing_values()

