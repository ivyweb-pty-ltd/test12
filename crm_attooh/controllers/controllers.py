# -*- coding: utf-8 -*-
from odoo import http


class WebsiteSign(http.Controller):
    @http.route(['/send_sms/<int:id>/<token>'], type='json', auth='public')
    def sign(self, id, token):
        request_item = http.request.env['signature.request.item'].sudo().search([('signature_request_id', '=', id), ('access_token', '=', token), ('state', '=', 'sent')], limit=1)
        return request_item.send_sms()