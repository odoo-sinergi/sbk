
from odoo import models
from odoo import http,tools,_
import json
from odoo.http import content_disposition, dispatch_rpc, request
from datetime import datetime, time
from odoo.tools.misc import DEFAULT_SERVER_TIME_FORMAT

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        """ Overrides community to prevent unnecessary load_menus request """
        return {
            'session_info': json.dumps(self.session_info()),
        }

    def session_info(self):
        ICP = request.env['ir.config_parameter'].sudo()
        User = request.env['res.users']

        if User.has_group('base.group_system'):
            warn_enterprise = 'admin'
        elif User.has_group('base.group_user'):
            warn_enterprise = 'user'
        else:
            warn_enterprise = False

        result = super(Http, self).session_info()
        result['warning'] = 'It will never expire' #warn_enterprise
        result['expiration_date'] = '3099-12-31'  #ICP.get_param('database.expiration_date')
        result['expiration_reason'] = 'No reason'  #ICP.get_param('database.expiration_reason')
        return result