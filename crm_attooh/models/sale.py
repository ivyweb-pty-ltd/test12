# -*- coding:utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_acceptance = fields.Selection([
        ('100', '100'),
        ('50', '50'),
    ], string="Payment % on Acceptance", default='50')
    payment_on_acceptance = fields.Monetary(compute='_compute_payment_amount', string='Payment on Acceptance')
    payment_on_completion = fields.Monetary(compute='_compute_payment_amount', string='Payment on Completion')

    def _compute_payment_amount(self):
        for order in self:
            payment_on_acceptance = payment_on_completion = 0.00
            if order.payment_acceptance == '50':
                payment_on_acceptance = (order.amount_total * 50.00) / 100.00
                payment_on_completion = (order.amount_total * 50.00) / 100.00
            elif order.payment_acceptance == '100':
                payment_on_acceptance = order.amount_total
                payment_on_completion = 0.00
            order.payment_on_acceptance = payment_on_acceptance
            order.payment_on_completion = payment_on_completion
