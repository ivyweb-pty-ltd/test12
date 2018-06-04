from odoo import http, _
from odoo.http import request
import base64
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal

class CustomerPortal(CustomerPortal):
    
    @http.route('/upload_document_helpdesk', type='http', auth="public", website=True)
    def upload_document_helpdesk(self, **post):
        filename = post.get('doc_attachment').filename
        file = post.get('doc_attachment')
        attach_id = request.env['ir.attachment'].create({
                        'name' : filename,
                        'type': 'binary',
                        'datas_fname':filename,
                        'datas': base64.b64encode(file.read()),
                        'document_available': True,
                        'document_type': post.get('doc_type'),
                        'res_id': post.get('ticket_id', False),
                        'res_model': 'helpdesk.ticket',
#                         'create_uid': request.env.user.id,
                    })
        attach_id._compute_res_name()
        print ('\n\nattach_id', attach_id)
        mail_msg_id = request.env['mail.message'].sudo().create({'attachment_ids': [(4, attach_id.id)],
                                                       'author_id': request.env.user.partner_id.id,
                                                       'model': 'helpdesk.ticket',
                                                       'res_id': int(post.get('ticket_id', False)),
                                                       'message_type': 'comment',
                                                       'website_published': True,
                                                       'create_uid': request.env.user.id,
                                                       })
        print ('\n\nmail_msg_id', mail_msg_id)
#         mail_msg_id.sudo().update({'create_uid': request.env.user.id})
#         print ('\n\ncurrent_user_id', request.env.user.id)
        return request.redirect('/helpdesk/ticket/%s'%post.get('ticket_id'))