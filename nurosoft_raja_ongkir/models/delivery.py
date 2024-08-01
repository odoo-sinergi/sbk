from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests

class SaleOrder(models.Model):
    _inherit = 'sale.order'    

    raja_ongkir_name = fields.Char(string='Ekspedisi')
    raja_ongkir_description = fields.Char(string='Layanan')
    raja_ongkir_city = fields.Char(string='Tujuan Pengiriman')
    raja_ongkir_etd = fields.Char(string='Perkiraan Sampai')
    raja_ongkir_value = fields.Float(string='Biaya')
    raja_ongkir_weight = fields.Float(string='Berat (gram)')
    delivery_type = fields.Selection(related='carrier_id.delivery_type')

    def write(self,vals):
        result = super(SaleOrder, self).write(vals)
        if 'carrier_id' in vals:
            carrier_id = vals['carrier_id']
            carrier = self.env['delivery.carrier'].browse(carrier_id)
            if carrier.delivery_type == 'raja_ongkir':
                total_weight = sum((line.product_id.weight*1000) * line.product_uom_qty for line in self.order_line)
                self.raja_ongkir_weight = total_weight
        return result

    def _check_carrier_quotation(self, force_carrier_id=None, post=None, keep_carrier=False):
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']

        if self.only_services:
            self._remove_delivery_line()
            return True
        else:
            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id and not keep_carrier:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id

            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            available_carriers = self._get_delivery_methods()
            if carrier:
                if carrier not in available_carriers:
                    carrier = DeliveryCarrier
                else:
                    # set the forced carrier at the beginning of the list to be verfied first below
                    available_carriers -= carrier
                    available_carriers = carrier + available_carriers
            if force_carrier_id or not carrier or carrier not in available_carriers:
                for delivery in available_carriers:
                    verified_carrier = delivery._match_address(self.partner_shipping_id)
                    if verified_carrier:
                        carrier = delivery
                        break
                self.write({'carrier_id': carrier.id})
            self._remove_delivery_line()
            if carrier and post:
                if carrier.delivery_type == 'raja_ongkir' and post.get('name', False):
                    split_city = post.get('city').split("->")
                    self.write({
                        'carrier_id': carrier.id,
                        'raja_ongkir_name': post.get('name'),
                        'raja_ongkir_description': post.get('description'),
                        'raja_ongkir_etd': post.get('etd') + 'HARI',
                        'raja_ongkir_value': self.env.ref('base.IDR').compute(post.get('value'), self.currency_id),
                        'raja_ongkir_city': split_city[1],
                        'raja_ongkir_weight': post.get('weight')
                    })
                res = carrier.rate_shipment(self)
                if res.get('success'):
                    self.set_delivery_line(carrier, res['price'])
                    self.delivery_rating_success = True
                    self.delivery_message = res['warning_message']
                else:
                    self.set_delivery_line(carrier, 0.0)
                    self.delivery_rating_success = False
                    self.delivery_message = res['error_message']

        return bool(carrier)

    def action_open_delivery_wizard(self):
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        carrier = (
            self.with_company(self.company_id).partner_shipping_id.property_delivery_carrier_id
            or self.with_company(self.company_id).partner_shipping_id.commercial_partner_id.property_delivery_carrier_id
        )
        if self.env.context.get('carrier_recompute'):
            name = _('Update shipping cost')
        else:
            name = _('Add a shipping method')
        
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_carrier_id': carrier.id,
            }
        }

class RajaOngkir(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('raja_ongkir', "Raja Ongkir")], ondelete={'raja_ongkir': 'set default'})
    raja_ongkir_api_key = fields.Char(string="API Key")
    raja_ongkir_account_type = fields.Selection([
           ('starter','Starter'),
           ('basic','Basic'),
           ('pro','Pro'),
        ],string="Tipe Akun", default="starter")
    raja_ongkir_origin_type = fields.Selection([
           ('city','Kabupaten/Kota'),
           ('subdistrict','Kecamatan'),
        ],string="Tipe Kota Asal", default='city')
    raja_ongkir_destination_type = fields.Selection([
           ('city','Kabupaten/Kota'),
           ('subdistrict','Kecamatan'),
        ],string="Tipe Kota Tujuan", default='city')
    raja_ongkir_city_origin_id = fields.Many2one(
        comodel_name='raja.ongkir.city',
        string="Kabupaten / Kota Asal")
    raja_ongkir_subdistrict_origin_id = fields.Many2one(
        comodel_name='raja.ongkir.subdistrict',
        string="Kecamatan Asal")

    def raja_ongkir_rate_shipment(self, order):
        return {
            'success': True,
            'price': order.raja_ongkir_value,
            'error_message': False,
            'warning_message': False,
        }

    def raja_ongkir_action_update_city(self):
        headers = {
            'key': self.raja_ongkir_api_key,
        }

        response = requests.get(self.raja_ongkir_get_city_data_url(), headers=headers)

        if response.status_code == 200:
            response_data = response.json()

            if response_data['rajaongkir']['status']['code'] == 200:
                for data in response_data['rajaongkir']['results']:
                    city = self.env['raja.ongkir.city'].search([('city_id','=',data['city_id'])],limit=1)
                    if city:
                        city.name = data['city_name']
                        city.type = data['type']
                        city.postal_code = data['postal_code']
                    else:
                        vals = {
                            'name' : data['city_name'],
                            'province_id' : data['province_id'],
                            'city_id' : data['city_id'],
                            'province' : data['province'],
                            'type' : data['type'],
                            'postal_code' : data['postal_code'],
                        }
                        city = self.env['raja.ongkir.city'].create(vals)
            
                return {
                    'name': _('Daftar Kabupaten/Kota'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'raja.ongkir.city',
                    'target': 'current',
                }
            else:
                raise UserError(response_data['rajaongkir']['status']['description'])
        else:
            raise UserError('Something wrong. Please try again.')

    def raja_ongkir_action_update_subdisctrict(self):
        cities = self.env['raja.ongkir.city'].search([])
        for city in cities:
            headers = {
                'key': self.raja_ongkir_api_key,
            }

            payload = {'city': city.city_id}

            response = requests.get(self.raja_ongkir_get_subdistrict_data_url(), headers=headers, params=payload)
            

            if response.status_code == 200:
                response_data = response.json()

                if response_data['rajaongkir']['status']['code'] == 200:
                    for data in response_data['rajaongkir']['results']:
                        subdistrict = self.env['raja.ongkir.subdistrict'].search([('subdistrict_id','=',data['subdistrict_id'])],limit=1)
                        if subdistrict:
                            subdistrict.name = data['subdistrict_name']
                            subdistrict.city = data['city']
                            subdistrict.city_type = data['type']
                            subdistrict.province = data['province']
                        else:
                            vals = {
                                'name' : data['subdistrict_name'],
                                'subdistrict_id' : data['subdistrict_id'],
                                'city' : data['city'],
                                'city_type' : data['type'],
                                'province' : data['province'],
                            }
                            subdistrict = self.env['raja.ongkir.subdistrict'].create(vals)               
                    
                else:
                    raise UserError(response_data['rajaongkir']['status']['description'])
            else:
                raise UserError('Something wrong. Please try again.')

        return {
                'name': _('Daftar Kecamatan'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'raja.ongkir.subdistrict',
                'target': 'current',
            }

    def raja_ongkir_check_cost(self, order, **post):
        if self.raja_ongkir_destination_type == 'city':
            city = order.partner_shipping_id.raja_ongkir_city_id.city_id if order.partner_shipping_id.raja_ongkir_city_id else False
        else:
            city = order.partner_shipping_id.raja_ongkir_subdistrict_id.subdistrict_id if order.partner_shipping_id.raja_ongkir_subdistrict_id else False
        
        if not city:
            return {
                'rajaongkir': {
                    'status': {
                        'status': 400,
                        'description': 'Maaf alamat pengiriman Anda "' + order.partner_shipping_id.city + '" tidak tersedia. Tolong pilih alamat pengiriman yang valid.'
                        }
                    }
            }

        ekspedisi = post['ekspedisi']

        
        headers = {
            'key': self.raja_ongkir_api_key,
            'content-type': "application/x-www-form-urlencoded"
        }

        total_weight = sum([(line.product_id.weight * line.product_qty) for line in order.order_line]) * 1000
        total_weight = int(round(total_weight))
        
        body = {}

        if self.raja_ongkir_account_type == 'pro':
            body = {
                'courier': ekspedisi,
                'origin': self.raja_ongkir_city_origin_id.city_id if self.raja_ongkir_origin_type == 'city' else self.raja_ongkir_subdistrict_origin_id.subdistrict_id,
                'originType': self.raja_ongkir_origin_type,
                'destinationType': self.raja_ongkir_destination_type,
                'destination': city,
                'weight': total_weight
            }

        else:
            body = {
                'courier': ekspedisi,
                'origin': self.raja_ongkir_city_origin_id.city_id,
                'destination': city,
                'weight': total_weight
            }
        
        response = requests.post(self.raja_ongkir_get_cost_data_url(), headers=headers, data=body)

        return response.json()

    def raja_ongkir_get_city_data_url(self):
        if self.raja_ongkir_account_type == 'starter':
            return 'https://api.rajaongkir.com/starter/city'

        if self.raja_ongkir_account_type == 'basic':
            return 'https://api.rajaongkir.com/basic/city'

        if self.raja_ongkir_account_type == 'pro':
            return 'https://pro.rajaongkir.com/api/city'

    def raja_ongkir_get_cost_data_url(self):
        if self.raja_ongkir_account_type == 'starter':
            return 'https://api.rajaongkir.com/starter/cost'

        if self.raja_ongkir_account_type == 'basic':
            return 'https://api.rajaongkir.com/basic/cost'

        if self.raja_ongkir_account_type == 'pro':
            return 'https://pro.rajaongkir.com/api/cost'

    def raja_ongkir_get_subdistrict_data_url(self):
        if self.raja_ongkir_account_type == 'pro':
            return 'https://pro.rajaongkir.com/api/subdistrict'
        else:
            raise ValidationError('Only Pro Account can use this feature')

    @api.constrains('delivery_type')
    def constrains_raja_ongkir(self):
        if self.delivery_type == 'raja_ongkir':
            get_another_raja_ongkir = self.env['delivery.carrier'].search([('delivery_type','=','raja_ongkir'),('id','!=',self._origin.id)])
            if get_another_raja_ongkir:
                raise ValidationError("There is other shipping method used Raja Ongkir. Please archive/delete it first.")

class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    jenis_layanan_rel = fields.Many2one('jenis.layanan',string='Jenis Layanan')
    cost_layanan = fields.Float(string='Cost', compute='compute_cost_layanan', readonly=True, store=True)

    @api.depends('jenis_layanan_rel')
    def compute_cost_layanan(self):
        for rec in self:
            if rec.jenis_layanan_rel:
                if rec.currency_id.id != self.env.ref('base.IDR').id:
                    rec.cost_layanan = self.env.ref('base.IDR').compute(rec.jenis_layanan_rel.price, rec.currency_id)
                else:
                    rec.cost_layanan = rec.jenis_layanan_rel.price
            else:
                rec.cost_layanan = 0

    @api.model
    def choose_layanan(self):
        self.delivery_message = False
        self.env['jenis.layanan'].search([]).unlink()
        if self.delivery_type=='raja_ongkir':
            res = self.carrier_id.rate_shipment(self.order_id)
            free_over = res.get('warning_message')
            check_cost = self.raja_ongkir_check_cost(self.order_id)
            list_ids_layanan = []
            for item in check_cost:
                results = item.get('rajaongkir', {}).get('results', [])
                for result in results:
                    code = result.get('code', '')
                    for cost in result.get('costs', []):
                        service = cost.get('service', '')
                        cost_value = cost.get('cost', [])[0].get('value', 0)
                        etd = cost.get('cost', [])[0].get('etd', '')
                        if code.upper() == 'POS':
                            formatted_label = f"{code.upper()} - {service} - Rp.{cost_value} [{etd}]"
                        else:
                            formatted_label = f"{code.upper()} - {service} - Rp.{cost_value} [{etd} Hari]"
                        search_layanan = self.env['jenis.layanan'].search([('layanan', '=', formatted_label)])
                        if free_over :
                            self.env['jenis.layanan'].create({'layanan':formatted_label,
                                                          'price':0})
                        else:
                            self.env['jenis.layanan'].create({'layanan':formatted_label,
                                                          'price':cost_value})
    
    def raja_ongkir_check_cost(self, order):
        # raja_ongkir = self.env['delivery.carrier'].search([('delivery_type','=','raja_ongkir')])
        raja_ongkir = self.carrier_id
        if raja_ongkir.raja_ongkir_destination_type == 'city':
            delivery_city = order.partner_shipping_id.city
            words_city = delivery_city.split()
            if words_city and words_city[0].lower() in ['kota', 'kabupaten']:
                find_city_code_1 = self.env['raja.ongkir.city'].search([('name','=ilike',f"%{words_city[1]}%")])
                if len(find_city_code_1.ids) == 1:
                    if find_city_code_1.type.lower() !=  words_city[0].lower():
                        raise ValidationError(delivery_city + " is not available. Please type the correct city in your delivery address")
                    city = find_city_code_1.id
                else:
                    find_city_code_2 = next(city for city in find_city_code_1 if city.type.lower() == words_city[0].lower())
                    if find_city_code_2.type.lower() !=  words_city[0].lower():
                        raise ValidationError(delivery_city + " is not available. Please type the correct city in your delivery address")
                    city = find_city_code_2.id
            else :
                find_city_code = self.env['raja.ongkir.city'].search([('name', 'ilike', f"%{delivery_city}%")])
                city = find_city_code[0].id if delivery_city and len(find_city_code) > 0 else False
        else:
            city = order.partner_shipping_id.raja_ongkir_subdistrict_id.subdistrict_id if order.partner_shipping_id.raja_ongkir_subdistrict_id else False

        if not city:
            raise ValidationError( delivery_city + " is not available. Please type the correct city in your delivery address")

        ekspedisi = ['jne','tiki','pos']
        headers = {
            'key': raja_ongkir.raja_ongkir_api_key,
            'content-type': "application/x-www-form-urlencoded"
        }
        total_weight = sum([(line.product_id.weight * line.product_qty) for line in order.order_line]) * 1000
        total_weight = int(round(total_weight))
        
        body = {}
        response_list=[]
        if raja_ongkir.raja_ongkir_account_type == 'pro':
            for kurir in ekspedisi:
                body = {
                    'courier': kurir,
                    'origin': raja_ongkir.raja_ongkir_city_origin_id.city_id if raja_ongkir.raja_ongkir_origin_type == 'city' else raja_ongkir.raja_ongkir_subdistrict_origin_id.subdistrict_id,
                    'originType': raja_ongkir.raja_ongkir_origin_type,
                    'destinationType': raja_ongkir.raja_ongkir_destination_type,
                    'destination': city,
                    'weight': total_weight
                }
                response = requests.post(raja_ongkir.raja_ongkir_get_cost_data_url(), headers=headers, data=body)
                res= response.json()
                if res.get('rajaongkir').get('status').get('code') == 400:
                    if res.get('rajaongkir').get('status').get('description') == 'Bad request. Origin harus diisi':
                        raise ValidationError('Bad request. Kabupaten/Kota Asal harus diisi')
                    else:
                        raise ValidationError(res.get('rajaongkir').get('status').get('description'))
                response_list.append(res)
        else:
            for kurir in ekspedisi:
                body = {
                    'courier': kurir,
                    'origin': raja_ongkir.raja_ongkir_city_origin_id.city_id,
                    'destination': city,
                    'weight': total_weight
                }
                response = requests.post(raja_ongkir.raja_ongkir_get_cost_data_url(), headers=headers, data=body)
                res= response.json()
                if res.get('rajaongkir').get('status').get('code') == 400:
                    if res.get('rajaongkir').get('status').get('description') == 'Bad request. Origin harus diisi':
                        raise ValidationError('Bad request. Kabupaten/Kota Asal harus diisi')
                    else:
                        raise ValidationError(res.get('rajaongkir').get('status').get('description'))
                response_list.append(res)
        return response_list
    
    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        self.delivery_message = False
        self.choose_layanan()
        if not self.carrier_id and not self.order_id.partner_shipping_id.property_delivery_carrier_id:
            raise UserError('Delivery method in delivery address cannot be empty.')
        vals = self._get_shipment_rate()
        if self.delivery_type in ('fixed', 'base_on_rule'):
            if vals.get('error_message'):
                return {'error': vals['error_message']}
        else:
            self.display_price = 0
            self.delivery_price = 0
    
    def button_confirm(self):
        try:
            if self.carrier_id.delivery_type =='raja_ongkir':
                self.order_id.set_delivery_line(self.carrier_id, self.cost_layanan)
                carrier_split =  self.jenis_layanan_rel.layanan.split("-")
                self.order_id.write({
                    'recompute_delivery_price': False,
                    'delivery_message': self.delivery_message,
                    'raja_ongkir_name': carrier_split[0],
                    'raja_ongkir_description' : carrier_split[1],
                    'raja_ongkir_etd' : carrier_split[2].split("[")[1].split("]")[0],
                    'raja_ongkir_city' : self.order_id.partner_shipping_id.city,
                    'raja_ongkir_value' : self.env.ref('base.IDR').compute(self.jenis_layanan_rel.price, self.currency_id),
                })
            else:
                self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
                self.order_id.write({
                    'recompute_delivery_price': False,
                    'delivery_message': self.delivery_message,
                })
        except Exception as e:
            print(f"An error occurred: {str(e)}")

class JenisLayanan(models.Model):
    _name = 'jenis.layanan'

    layanan = fields.Char(string='Jenis Layanan')
    price = fields.Float(string='Cost')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.layanan))
        return result

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def send_to_shipper(self):
        self.ensure_one()
        if self.carrier_id.delivery_type == 'raja_ongkir':
            orderline=self.env['sale.order.line'].search([('order_id','=',self.sale_id.id)])
            price_rajaongkir = 0.0 

            for line in orderline:
                if "raja ongkir" in line.name.lower():
                    price_rajaongkir += line.price_total
            res = {'exact_price': price_rajaongkir, 'tracking_number': False}
        else:
            res = self.carrier_id.send_shipping(self)[0]
            
        if self.carrier_id.free_over and self.sale_id and self.sale_id._compute_amount_total_without_delivery() >= self.carrier_id.amount:
            res['exact_price'] = 0.0
        self.carrier_price = res['exact_price'] * (1.0 + (self.carrier_id.margin / 100.0))
        if res['tracking_number']:
            previous_pickings = self.env['stock.picking']
            previous_moves = self.move_lines.move_orig_ids
            while previous_moves:
                previous_pickings |= previous_moves.picking_id
                previous_moves = previous_moves.move_orig_ids
            without_tracking = previous_pickings.filtered(lambda p: not p.carrier_tracking_ref)
            (self + without_tracking).carrier_tracking_ref = res['tracking_number']
            for p in previous_pickings - without_tracking:
                p.carrier_tracking_ref += "," + res['tracking_number']
        order_currency = self.sale_id.currency_id or self.company_id.currency_id
        msg = _(
            "Shipment sent to carrier %(carrier_name)s for shipping with tracking number %(ref)s<br/>Cost: %(price).2f %(currency)s",
            carrier_name=self.carrier_id.name,
            ref=self.carrier_tracking_ref,
            price=self.carrier_price,
            currency=order_currency.name
        )
        self.message_post(body=msg)
        self._add_delivery_cost_to_so()
