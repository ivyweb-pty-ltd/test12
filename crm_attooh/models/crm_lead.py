# -*- coding: utf-8 -*-
import base64
import io
import random
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from odoo.modules.module import get_module_resource

from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, timedelta
from odoo.exceptions import UserError
#from odoo.addons.website_sign.models.signature_request import SignatureRequestItem

#TODO: Load Data for all the possible product_types

class SignatureRequest(models.Model):
    _inherit = 'signature.request'

    lead_id = fields.Many2one('crm.lead')

    @api.model
    def initialize_sign_new(self, id, signers, followers, lead_id, reference, subject, message, record=False, send=True):
        signature_request = self.create(
            {'template_id': id, 'reference': reference, 'lead_id': lead_id, 'follower_ids': [(6, 0, followers)],
             'favorited_ids': [(4, self.env.user.id)]})
        signature_request.set_signers(signers)
        if send:
            signature_request.action_sent(subject, message)
            signature_request._message_post(_('Waiting for signatures.'), type='comment', subtype='mt_comment')
        if record:
            body = _('%s has been sent to %s') % (subject, record.partner_id.name)
            record.message_post(body, message_type='comment')
        return {
            'id': signature_request.id,
            'token': signature_request.access_token,
            'sign_token': signature_request.request_item_ids.filtered(
                lambda r: r.partner_id == self.env.user.partner_id).access_token,
        }


    @api.one
    def generate_completed_document(self):
        if len(self.template_id.signature_item_ids) <= 0:
            self.completed_document = self.template_id.attachment_id.datas
            return

        old_pdf = PdfFileReader(io.BytesIO(base64.b64decode(self.template_id.attachment_id.datas)), overwriteWarnings=False)
        font = "Helvetica"
        normalFontSize = 0.015

        packet = io.BytesIO()
        can = canvas.Canvas(packet)
        itemsByPage = self.template_id.signature_item_ids.getByPage()
        SignatureItemValue = self.env['signature.item.value']
        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            width = float(page.mediaBox.getUpperRight_x())
            height = float(page.mediaBox.getUpperRight_y())

            # Set page orientation (either 0, 90, 180 or 270)
            rotation = page.get('/Rotate')
            if rotation:
                can.rotate(rotation)
                # Translate system so that elements are placed correctly
                # despite of the orientation
                if rotation == 90:
                    width, height = height, width
                    can.translate(0, -height)
                elif rotation == 180:
                    can.translate(-width, -height)
                elif rotation == 270:
                    width, height = height, width
                    can.translate(-width, 0)

            items = itemsByPage[p + 1] if p + 1 in itemsByPage else []
            for item in items:
                value = SignatureItemValue.search([('signature_item_id', '=', item.id), ('signature_request_id', '=', self.id)], limit=1)
                if not value or not value.value:
                    continue

                value = value.value

                if item.type_id.type == "text":
                    can.setFont(font, height * item.height * 0.8)
                    can.drawString(width * item.posX, height * (1 - item.posY - item.height * 0.9), value)

                elif item.type_id.type == "textarea":
                    can.setFont(font, height * normalFontSize * 0.8)
                    lines = value.split('\n')
                    y = (1 - item.posY)
                    for line in lines:
                        y -= normalFontSize * 0.9
                        can.drawString(width * item.posX, height * y, line)
                        y -= normalFontSize * 0.1

                elif item.type_id.type == "signature" or item.type_id.type == "initial":
                    img = base64.b64decode(value[value.find(',') + 1:])
                    can.drawImage(ImageReader(io.BytesIO(img)), width * item.posX, height * (1 - item.posY - item.height), width * item.width, height * item.height, 'auto', True)

                elif item.type_id.type == "checkbox":
                    symboia_font_family = get_module_resource('crm_attooh', 'fonts', 'Symbola_hint.ttf')
                    symbola_font = TTFont('Symbola', symboia_font_family)
                    pdfmetrics.registerFont(symbola_font)
                    styles = getSampleStyleSheet()
                    styles["Title"].fontName = 'Symbola'
                    can.setFont('Symbola', height * item.height * 0.5)
                    if value == "True":
                        can.drawString(width * item.posX, height * (1 - item.posY - item.height * 0.9), '\u2611')
                    else:
                        can.drawString(width * item.posX, height * (1 - item.posY - item.height * 0.9), '\u2610')
            can.showPage()
        can.save()

        item_pdf = PdfFileReader(packet, overwriteWarnings=False)
        new_pdf = PdfFileWriter()

        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            page.mergePage(item_pdf.getPage(p))
            new_pdf.addPage(page)

        output = io.BytesIO()
        new_pdf.write(output)
        self.completed_document = base64.b64encode(output.getvalue())
        output.close()

class SignatureItemTypeAttooh(models.Model):
    _inherit = "signature.item.type"

    type = fields.Selection(selection_add=[('checkbox', 'Checkbox')])


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    service_ids = fields.Many2many('crm.service.type', related='partner_id.service_ids',string='Provided Services')
    activity_type_ids = fields.Many2one('crm.service.type.activity')
    signature_requests_count = fields.Integer("# Signature Requests", compute='_compute_signature_requests')
    signature_ids = fields.One2many('signature.request', 'lead_id')
    product_area_id = fields.Many2one('crm.service.type',string='Product Area')


    service_activity_ids = fields.One2many('crm.service.activity','lead_id')
    referred = fields.Many2one('res.partner', 'Referred By')
    financial_product_id = fields.Many2one('financial_product')

    contract_policy_number = fields.Char('Contract/Policy Number',related="financial_product_id.contract_policy_number")
    submission_date = fields.Date('Submission Date',related="financial_product_id.submission_date")
    date_of_issue = fields.Date('Date of Issue',related="financial_product_id.date_of_issue")
    doc = fields.Date('DOC',related="financial_product_id.doc")
    compliance_mail = fields.Date('Compliance Mail',related="financial_product_id.compliance_mail")
    product_provider_id = fields.Many2one('res.partner', related="financial_product_id.product_provider_id")
    product_id = fields.Many2one('product.template', 'Product',related="financial_product_id.product_id")
    premium = fields.Float('Premium',related="financial_product_id.premium")
    vitality = fields.Boolean('Vitality',related="financial_product_id.vitality")
    fica = fields.Boolean('FICA',related="financial_product_id.fica")
    commission_year_1 = fields.Float('1st year Commission',related="financial_product_id.commission_year_1")
    commission_year_2 = fields.Float('2nd year Commission',related="financial_product_id.commission_year_2")
    monthly_commission = fields.Float(' Monthly Ongoing Commission',related="financial_product_id.monthly_commission")
    issued_commission_year_1 = fields.Float('Issued 1st year Commission',related="financial_product_id.issued_commission_year_1")
    issued_commission_year_2 = fields.Float('Issued 2nd year Commission',related="financial_product_id.issued_commission_year_2")
    issued_monthly_commission = fields.Float('Issued Monthly Ongoing Commission',related="financial_product_id.issued_monthly_commission")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id,related="financial_product_id.currency_id")
    book_notes = fields.Text('Production Book Notes',related="financial_product_id.book_notes")


    # string changes on existing fields
    phone = fields.Char('Work Phone')
    # team_id = fields.Many2one(string='Sales to New Business')
    sms_on_lead = fields.Boolean(compute="_compute_sms_on_lead")
    sms_on_opportunity = fields.Boolean(compute="_compute_sms_on_opportunity")
    responsible_id = fields.Many2one('res.users','Responsible')


#    @api.onchange('partner_id')
    def set_partner_id(self):
        for item in self:
            if not item.financial_product_id:
                financial_product_id=item.financial_product_id.create({"partner_id":item.partner_id.id})
            else:
                financial_product_id=item.financial_product_id
            financial_product_id.write({"partner_id": item.partner_id.id})
            item.write({'financial_product_id':financial_product_id.id})

    def _compute_sms_on_lead(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sms_on_lead = ICPSudo.get_param('crm_attooh.sms_on_lead')
        for lead in self:
            lead.sms_on_lead = sms_on_lead

    def _compute_sms_on_opportunity(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sms_on_opportunity = ICPSudo.get_param('crm_attooh.sms_on_opportunity')
        for lead in self:
            lead.sms_on_opportunity = sms_on_opportunity

    @api.multi
    def sms_action(self):
        self.ensure_one()
        if not self.mobile:
            raise UserError(_("Please enter mobile number."))
        default_mobile = self.env.ref('sms_frame.sms_number_default')
        return {
            'name': 'SMS Compose',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sms.compose',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_from_mobile_id': default_mobile.id, 'default_to_number': self.mobile, 'default_record_id': self.id, 'default_model': 'crm.lead'}
        }

    @api.multi
    def get_user_id(self, activity):
        user_id = False
        user_id = activity.employee_role_id.employee_id and activity.employee_role_id.employee_id.id or False
        return user_id

    @api.model
    def create(self,vals={}):
        fp_vals={}
        if 'partner_id' in vals:
            fp_vals['partner_id']=vals['partner_id']
        if 'user_id' in vals:
            fp_vals['user_id']=vals['user_id']
        financial_product_id=self.env['financial_product'].create(fp_vals)
        vals['financial_product_id']=financial_product_id.id
        res = super(crm_lead, self).create(vals)
        financial_product_id.crm_lead_id=res.id
        return res

    @api.depends('service_activity_ids','responsible_id','stage_id')
    def _activities_changed(self):
        self.activity_ids.lead_id=1
        return

    @api.one
    def write(self, vals):
        # TODO: Set partner_id correctly on write for financial_service_product

        operation_list = []

        #Create relevant mail activities
        if self.service_activity_ids.search_count([('lead_id','=',self.id),('mail_activity_id','!=',False)])==0:
            v2=self.next_activity(resource_id=self.id)
            if v2:
                vals.update(v2)

        if self.financial_product_id:
            if ('partner_id' in vals):
                self.financial_product_id.partner_id=vals['partner_id']

            self.financial_product_id.crm_lead_id=self.id

            if ('user_id' in vals):
                self.financial_product_id.user_id=vals['user_id']

        res = super(crm_lead, self).write(vals)
        return res

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

    @api.onchange('product_area_id')
    def change_product_area(self):

        operation_list = []

        #Delete all activities that was not completed. Also delete the mail activities attached to these
        for activity_item in self.service_activity_ids:
            if activity_item.mail_activity_id:
                activity_item.mail_activity_id.unlink()
            if activity_item.completed==True:
                operation_list.append(activity_item.id)

        #Add all activities related to the specific product area
        for add_activity in self.product_area_id.service_type_activity_ids:
            user_employee_role=self.env['user.employee.roles'].search([('employee_role_id','=',add_activity.employee_role_id.id)],limit=1)

            temp_id=self.env['crm.service.activity'].create({
                                        'name': add_activity.name,
                                        'service_type_activity_id': add_activity.id,
                                        'lead_id': self._origin.id,
                                        'completed' : False,
                                        'employee_role_id': add_activity.employee_role_id.id,
                                        'user_id': user_employee_role.employee_id.id,
                                        'sequence' : add_activity.sequence,
                                        })
            operation_list.append(temp_id.id)

        self.service_activity_ids=[(6,0,operation_list)]

        if (self.financial_product_id):
            if (self.partner_id and self.financial_product_id):
                self.financial_product_id.partner_id=self.partner_id

            self.financial_product_id.crm_lead_id=self.id

            if (self.user_id and self.financial_product_id):
                self.financial_product_id.user_id=self.user_id
    @api.model
    def next_activity(self,activity_id=None,resource_id=None):
        vals={}
        if not resource_id:
            resource_id=self.id

        #TODO: If no other mail_activities attached create new mail_activity
        for item in self.service_activity_ids.search([('lead_id','=',resource_id),('completed','=',False)],order='sequence',limit=1):
            #TODO: Open next activity
            if item.service_type_activity_id.employee_role_id:
                user_id=item.service_type_activity_id.employee_role_id.employee_id.id
            elif item.user_id:
                user_id=item.user_id.id
            elif item.lead_id.responsible_id:
                user_id=item.lead_id.responsible_id.id
            elif item.lead_id.user_id:
                user_id=item.lead_id.user_id.id
            vals["responsible_id"]=user_id
            if item.service_type_activity_id.stage_id:
                vals['stage_id']=item.service_type_activity_id.stage_id.id
            if not item.mail_activity_id:
                new_activity_id=item.mail_activity_id.create({
                    'activity_type_id': item.service_type_activity_id.activity_type_id.id,
                    'res_id': resource_id,
                    'res_model_id': self.env.ref('crm.model_crm_lead').id,
                    'date_deadline': fields.datetime.now()+timedelta(hours=item.service_type_activity_id.lead_time),
                    'summary': item.name,
                    #TODO: Choose the right user to assign
                    'user_id': user_id,
                    'service_activity_id': item.id,
                })
                item.mail_activity_id=new_activity_id
            return vals


class CrmTeamAttooh(models.Model):
    _inherit = "crm.team"

#TODO: Build Product Type Manager
#TODO: Build data for product Types

class SignatureItemAtooh(models.Model):
    _inherit = 'signature.request.item'

    ip_address = fields.Char('Ip Address')
    country_name = fields.Char()
    country_code = fields.Char()
    city = fields.Char()
    region = fields.Char()
    time_zone = fields.Char()
    opt = fields.Char()

    @api.multi
    def action_completed(self):
        self.write({
            'country_name': request.session.get('geoip', {}).get('country_name'),
            'country_code': request.session.get('geoip', {}).get('country_code'),
            'city': request.session.get('geoip', {}).get('city'),
            'region': request.session.get('geoip', {}).get('region'),
            'time_zone': request.session.get('geoip', {}).get('time_zone'),
            'ip_address': request.httprequest.remote_addr
        })
        return super(SignatureItemAtooh, self).action_completed()


class CRMAttoohLeadType(models.Model):
    _name = "crm.service.type"

    name = fields.Char("Name")
    service_type_activity_ids =  fields.One2many('crm.service.type.activity','service_type_id')


class CRMActivity(models.Model):
    _name = "crm.service.activity"

    name = fields.Char('Process')
    lead_id = fields.Many2one('crm.lead')
    sequence = fields.Integer('Sequence')
    completed = fields.Boolean('Completed')
    service_type_activity_id = fields.Many2one('crm.service.type.activity',required=True)
    user_id = fields.Many2one('res.users',string='Assigned to User')
#                              domain=(['user_employee_roles_ids','in',service_type_activity_id.employee_role_id]))
    mail_activity_id = fields.Many2one('mail.activity')
    date_completed = fields.Datetime('Completed on')
    stage_id = fields.Many2one('crm.stage',related='service_type_activity_id.stage_id')
    employee_role_id = fields.Many2one('employee.roles', related='service_type_activity_id.employee_role_id')

class crm_service_type_activity(models.Model):
    _name = 'crm.service.type.activity'
    _description = 'Service Type Activity'

    stage_id = fields.Many2one('crm.stage', string='Stage', track_visibility='onchange', index=True)
    sequence = fields.Integer('Sequence')
    reference = fields.Char(string='Reference', required=True)
    name = fields.Char(string='Process', required=True)
    employee_role_id = fields.Many2one('employee.roles','Responsible')
    lead_time = fields.Float('Lead time',size=5)
    time_allocation = fields.Float('Time Allocation',size=5)
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity Type")
    service_type_id = fields.Many2one('crm.service.type', string="Service Type")
    document_ids = fields.Many2many('signature.request.template',relation='service_activity_type_documents',
                                    column1='service_type_activity_id',column2='signature_request_template_id')
    active = fields.Boolean(default=True)