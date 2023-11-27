from odoo.exceptions import UserError, ValidationError, Warning
from odoo.http import request
from oauthlib.oauth2.rfc6749 import errors
from odoo.http import request, Response
import json



def authenticate():
    """This method is based on auth2 authentication.
		It will authenticate the users token.
		params :
		Authorization: Authorization should be part of request header
		and it must include Bearer
		Return: It will raise error if token is invalid.

        To use this method import it in your controler 
        from odoo.addons.odoo_auth2.controllers.auth2_authentication import authenticate
        add authentication() in your controller: 

    """
    error ={}
    headers = dict(list(request.httprequest.headers.items()))
    authHeader = headers['Authorization']
    if authHeader.startswith("Bearer "):
        try:
            access_token = authHeader[7:]
            token = request.env['auth.access.token'].search([('access_token','=',access_token)])
            if not token or not token.is_valid():
                raise UserError("Access Token Invalid.")
            user = token.token_id.user_id
            db = request.session.db
            request.session.authenticate(db, user.sudo().login, access_token)
            return request.env['ir.http'].session_info()
        except Exception as e:
            raise e
    else:
        raise UserError("Access Token Invalid Start with Bearer")
   