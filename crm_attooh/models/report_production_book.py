# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ReportProuctionBook(models.AbstractModel):
    _name = 'report.production.book'
    _description = 'manage summary and footnotes of production book report'
    _inherit = 'account.report'

    def get_report_name(self):
        return _('Production Book')

    def get_columns_name(self, options):
        return [
            {},
            {'name': _('Product Provider')},
            {'name': _('Product')},
            {'name': _('1st year Commission'), 'class': 'number'},
            {'name': _('2st year Commission'), 'class': 'number'},
            {'name': _('Monthly Ongoing Commission'), 'class': 'number'},
            {'name': _('Date of Issue')},
            {'name': _('Vitality')},
            {'name': _('DOC Compliance Mail')},
            {'name': _('FICA')},
            {'name': _('Issued 1st year Commission')},
            {'name': _('Issued 2st year Commission')},
            {'name': _('Issued Monthly Ongoing Commission')},
            {'name': _('Salesperson')}
        ]

    @api.model
    def get_lines(self, options, line_id=None):
        lines = []
        for lead in self.env['crm.lead'].search([]):
            lines.append({
                'id': lead.id,
                'name': lead.partner_id.name,
                'columns': [
                    {'name': lead.product_provider_id.name},
                    {'name': lead.product_id.name},
                    {'name': lead.commission_year_1},
                    {'name': lead.commission_year_2},
                    {'name': lead.monthly_commission},
                    {'name': lead.date_of_issue},
                    {'name': lead.vitality and 'Yes' or 'No'},
                    {'name': lead.complience_mail},
                    {'name': lead.fica and 'Yes' or 'No'},
                    {'name': lead.issued_commission_year_1},
                    {'name': lead.issued_commission_year_2},
                    {'name': lead.issued_monthly_commission},
                    {'name': lead.user_id.name}
                ],
                'unfoldable': False,
                'unfolded': False,
            })
        return lines
