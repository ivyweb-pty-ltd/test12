# -*- coding: utf-8 -*-
#
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    @http.route(['/my/personalfinancial'], type='http', auth="user", website=True)
    def portal_my_personalfinance(self, meeting_id=None, edit_mode=None, **kw):
        partner = request.env.user.partner_id
        Income = request.env['partner.income']
        Expense = request.env['partner.expense']
        return request.render("crm_attooh.personalfinancial_detail", {
            'partner': partner,
            'edit_mode': edit_mode,
            'Income_obj': Income,
            'Expense': Expense
        })

