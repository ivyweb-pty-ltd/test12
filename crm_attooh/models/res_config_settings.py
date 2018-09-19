# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_crm_credit_report = fields.Boolean("XDS - Credit Bureau Integration")
    sms_on_lead = fields.Boolean("SMS On Lead")
    sms_on_opportunity = fields.Boolean("SMS On Opportunity")
    sms_on_ticket = fields.Boolean("SMS On Helpdesk Ticket")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update(
            sms_on_lead=ICPSudo.get_param('crm_attooh.sms_on_lead'),
            sms_on_opportunity=ICPSudo.get_param('crm_attooh.sms_on_opportunity'),
            sms_on_ticket=ICPSudo.get_param('crm_attooh.sms_on_ticket')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("crm_attooh.sms_on_lead", self.sms_on_lead)
        ICPSudo.set_param("crm_attooh.sms_on_opportunity", self.sms_on_opportunity)
        ICPSudo.set_param("crm_attooh.sms_on_ticket", self.sms_on_ticket)
