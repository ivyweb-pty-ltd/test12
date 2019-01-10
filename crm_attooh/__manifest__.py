# -*- coding: utf-8 -*-
{
    'name': "crm_attooh",

    'summary': """Customimsation for attooh""",

    'description': """
    """,

    'author': "Strategic Dimensions",
    'website': "https://www.strategicdimensions.co.za",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '3.1',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'sale_management', 'website_sign', 'website_quote', 'website_event',
    'website_form', 'helpdesk', 'base_automation', 'portal', 'hr', 'marketing_automation', 'attooh_sms'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res_partner_data.xml',
        'data/signature_item_type_data.xml',
        'data/helpdesk_data.xml',
        'data/ticket_type_activity_data.xml',
        'data/crm_demo.xml',
        'data/ticket_type_activity_data.xml',
        'data/crm_stage_data.xml',
        'data/crm.service.type.csv',
        'data/crm.service.type.activity.csv',
        'data/hr_employee_roles_data.xml',
        'data/partner.relationship_type.xml',
        'data/partner.relationship_type.csv',
        'views/crm_views.xml',
        'views/hr_views.xml',
        'views/res_partner_views.xml',
        'views/ir_attachment.xml',
        'views/res_config_settings_views.xml',
        'views/document_views.xml',
        'views/sale_views.xml',
        'views/stage_activity_view.xml',
        'views/ticket_type_activity_view.xml',
        'views/report_saleorder_document.xml',
        'views/website_quote_template.xml',
        'views/meeting_portal_template.xml',
        'views/signature_portal_template.xml',
        'views/document_portal_template.xml',
        'views/activity_portal_template.xml',
        'views/portal_my_detail.xml',
        'views/finance_portal_template.xml',
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_portal_templates.xml',
        'views/crm_reporting_view.xml',
        'views/res_users.xml',
        'views/crm_reporting_activity.xml',
        'views/mail_activity_views.xml',
        'views/event_template.xml',
        'views/report_production_book.xml',
        'views/financial_product_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'post_init_hook':'post_init_check',
    'application': True,
}
