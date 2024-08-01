from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    raja_ongkir_city_id = fields.Many2one('raja.ongkir.city', 'Raja Ongkir City')
    raja_ongkir_subdistrict_id = fields.Many2one('raja.ongkir.subdistrict', 'Raja Ongkir Subdisctrict')

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(city)s\n%(zip)s\n%(country_name)s"

    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        
        address_format = self._get_default_address_format() or \
            self.country_id.address_format
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.commercial_company_name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        
        return address_format % args
