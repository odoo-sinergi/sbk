# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import urllib


class City(models.Model):
    _name = 'raja.ongkir.city'

    name = fields.Char()
    province_id = fields.Integer()
    city_id = fields.Integer()
    province = fields.Char(string="Provinsi")
    type = fields.Char(string="Tipe")
    postal_code = fields.Char(string="Kode Pos")

class Ekpedisi(models.Model):
    _name = 'raja.ongkir.carrier'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    website_published = fields.Boolean(string="Published On Website",default=False)


    
    def website_publish_button(self):
        self.website_published = False if self.website_published else True


class Subdistrict(models.Model):
    _name = 'raja.ongkir.subdistrict'

    name = fields.Char(string="Name")
    city = fields.Char(string="City")
    city_type = fields.Char(string="Tipe Kabupaten Kota")
    province = fields.Char(string="Province")
    subdistrict_id = fields.Integer(string="Subdistrict ID")

class CekResi(models.Model):
    _name = 'raja.ongkir.waybill'

    carrier_id = fields.Many2one(
        comodel_name='raja.ongkir.carrier',
        string="Ekpedisi"
    )

    name = fields.Char(default="Cek Resi")

    waybill = fields.Char('No. Resi')

    service_code = fields.Char('Layanan')
    waybill_date = fields.Char('Date')
    shipper_name = fields.Char('Nama Pengirim')
    receiver_name = fields.Char('Nama Penerima')
    origin = fields.Char('Kota Asal')
    destination = fields.Char('Kota Tujuan')
    status = fields.Char('Status')

    
    def open_raja_ongkir_waybill(self):

        waybill = self.env['raja.ongkir.waybill'].search([],limit=1)
        if not waybill:
            waybill = self.env['raja.ongkir.waybill'].create({})
        return {
            'name': _('Cek Resi'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'res_model': 'raja.ongkir.waybill',
            'res_id': waybill.id,
            'target': 'current',
        }

    
    
    def check_waybill(self):
        if not self.waybill or not self.carrier_id:
            raise ValidationError('Pilih Ekpedisi dan isi No. Resi')
        raja_ongkir = self.env['delivery.carrier'].search([('delivery_type','=','raja_ongkir')],limit=1)
        headers = {
            'key': raja_ongkir.raja_ongkir_api_key,
        }

        body = {
            'waybill': self.waybill,
            'courier': self.carrier_id.code,
        }

        response = requests.post('https://pro.rajaongkir.com/api/waybill', headers=headers, data=body)

        if response.status_code == 200:
            response_data = response.json()
            
            if response_data['rajaongkir']['status']['code'] == 200:
                summary = response_data['rajaongkir']['result']['summary']
                self.write({
                        'service_code' : summary['service_code'],
                        'waybill_date' : summary['waybill_date'],
                        'shipper_name' : summary['shipper_name'],
                        'receiver_name' : summary['receiver_name'],
                        'origin' : summary['origin'],
                        'destination' : summary['destination'],
                        'status' : summary['status'],
                    })                   
            
                
            else:
                raise UserError(response_data['rajaongkir']['status']['description'])
        else:
            raise UserError('Something wrong. Please try again.')


# class AddCostCity(models.Model):
#     _name = 'raja.ongkir.city.cost'

#     city_id = fields.Many2one(
#         comodel_name='raja.ongkir.city',
#         string="Kabupaten / Kota Tujuan"
#     )

#     carrier_id = fields.Many2one(
#         comodel_name='raja.ongkir.carrier',
#         string="Ekpedisi"
#     )

#     service = fields.Char('Layanan')
#     additional_cost = fields.Float('Additional Cost', default=0)
#     fixed_cost = fields.Float('Additional Cost', default=0)





    