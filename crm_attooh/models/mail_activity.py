from odoo import models, fields, api, _
from datetime import date
from datetime import timedelta


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    service_activity_id = fields.Many2one('crm.service.activity')

    @api.model
    def create(self, values):
        # already compute default values to be sure those are computed using the current user
        values_w_defaults = self.default_get(self._fields.keys())
        values_w_defaults.update(values)

        # continue as sudo because activities are somewhat protected
        activity = super(models.Model, self.sudo()).create(values_w_defaults)
        activity_user = activity.sudo(self.env.user)
        activity_user._check_access('create')
        if activity.date_deadline <= fields.Date.today():
            self.env['bus.bus'].sendone(
                (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                {'type': 'activity_updated', 'activity_created': True})
        return activity_user

    @api.multi
    def action_feedback(self, feedback=False):
        for item in self:
            if item.service_activity_id:
                item.service_activity_id.completed=True
                item.service_activity_id.date_completed=fields.datetime.now()
            if item.service_activity_id.lead_id:
                item.service_activity_id.lead_id.next_activity()
        return super(MailActivity,self).action_feedback(feedback)



