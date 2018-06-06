# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class CrmAttooh(models.Model):
    _name = 'crm_attooh.service'

    name = fields.Char()

class SignatureRequest(models.Model):
    _inherit = 'signature.request'

    lead_id = fields.Many2one('crm.lead')
    
    @api.model
    def initialize_sign_new(self, id, signers, followers, lead_id, reference, subject, message, send=True):
        signature_request = self.create(
            {'template_id': id, 'reference': reference, 'lead_id': lead_id, 'follower_ids': [(6, 0, followers)],
             'favorited_ids': [(4, self.env.user.id)]})
        signature_request.set_signers(signers)
        if send:
            signature_request.action_sent(subject, message)
            signature_request._message_post(_('Waiting for signatures.'), type='comment', subtype='mt_comment')
        return {
            'id': signature_request.id,
            'token': signature_request.access_token,
            'sign_token': signature_request.request_item_ids.filtered(
                lambda r: r.partner_id == self.env.user.partner_id).access_token,
        }


class CRM(models.Model):
    _inherit = 'crm.lead'

    service_ids = fields.Many2many('crm_attooh.service', 'crm_lead_service_rel', 'lead_id', 'service_id',
                                   string='Services')
    signature_requests_count = fields.Integer("# Signature Requests", compute='_compute_signature_requests')
    signature_ids = fields.One2many('signature.request', 'lead_id')
    product_area = fields.Selection([
        ('financial_planning', 'Financial Planning'),
        ('short_term', 'Short Term'),
        ('health', 'Health'),
        ('investments', 'Investments'),
        ('risk', 'Risk')
    ], string="Product Area")
    referred = fields.Many2one('res.partner', 'Referred By')
    phone = fields.Char('Work Phone')

    @api.onchange('stage_id')
    def onchanhge_stage_id(self):
        user_id = False
        for activity in self.stage_id.stage_activity_ids:
            if self.team_id and activity.team_ids and self.team_id.id in activity.team_ids.ids:
                date_deadline = datetime.today() + timedelta(days=activity.activity_date)
                if activity.assign_to_owner:
                    user_id = self.user_id and self.user_id.id or False
                else:
                    user_id = activity.user_id and activity.user_id.id or False
                activities = self.env['mail.activity'].search(
                    [('res_id', '=', self._origin.id), ('stage_activity_id', '=', activity.id)])
                if not activities:
                    self.env['mail.activity'].sudo().create({
                        'activity_type_id': activity.activity_type_id and activity.activity_type_id.id or False,
                        'res_id': self._origin.id,
                        'res_model_id': self.env.ref('crm.model_crm_lead').id,
                        'date_deadline': date_deadline,
                        'summary': activity.name,
                        'user_id': user_id,
                        'stage_activity_id': activity.id,
                    })

        # TO FIX: why self.id is <odoo.models.NewId object >
        lead_id = self._context.get('params', {}).get('id')
        if lead_id:
            automate_emails = self.stage_id.stage_automated_email_ids.filtered(lambda r: r.user_id == self.user_id)
            for record in automate_emails:
                self.browse(lead_id).message_post_with_template(record.email_template_id.id)

        signature_requests = self.stage_id.stage_signature_request_ids.filtered(lambda r: r.user_id == self.user_id)
        for record in signature_requests:
            print('EEEE', record, record.signature_request_template_id)
            # self.browse(lead_id).message_post_with_template(record.email_template_id.id)

    @api.onchange('product_area')
    def onchanhge_product_area(self):
        if self.product_area == 'short_term':
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_1')
        elif self.product_area == 'health':
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_2')
        elif self.product_area == 'investments':
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_3')
        elif self.product_area == 'risk':
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_4')

    @api.multi
    def _compute_signature_requests(self):
        self.ensure_one()
        self.signature_requests_count = len(self.signature_ids)

    @api.multi
    def open_lead_signature(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id('website_sign', 'signature_request_action')
        action['domain'] = [('id', 'in', self.signature_ids.ids)]
        return action

