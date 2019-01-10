from odoo import api, models, fields

class financial_product(models.Model):

    _name = "financial_product"

    crm_lead_id = fields.Many2one('crm.lead') #TODO: Make sure that crm_lead_id is assigned
    user_id = fields.Many2one('res.users') #TODO: Make sure this is assigned from crm.lead
    partner_id = fields.Many2one('res.partner') #TODO: Make sure partner_id is assigned on from crm.lead
    contract_policy_number = fields.Char('Contract/Policy Number')
    submission_date = fields.Date('Submission Date')
    date_of_issue = fields.Date('Date of Issue')
    doc = fields.Date('DOC')
    compliance_mail = fields.Date('Compliance Mail')
    product_provider_id = fields.Many2one('res.partner', string='Product Provider', domain="[('supplier', '=', True)]")
    product_id = fields.Many2one('product.template', 'Product')
    premium = fields.Float('Premium')
    vitality = fields.Boolean('Vitality')
    fica = fields.Boolean('FICA')
    commission_year_1 = fields.Float('1st year Commission')
    commission_year_2 = fields.Float('2nd year Commission')
    monthly_commission = fields.Float(' Monthly Ongoing Commission')
    issued_commission_year_1 = fields.Float('Issued 1st year Commission')
    issued_commission_year_2 = fields.Float('Issued 2nd year Commission')
    issued_monthly_commission = fields.Float('Issued Monthly Ongoing Commission')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    book_notes = fields.Text('Production Book Notes')
