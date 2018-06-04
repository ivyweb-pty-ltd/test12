# -*- coding: utf-8 -*-
{
    'name': "crm_attooh",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'sale_management', 'website_sign', 'website_quote', 'website_form', 'helpdesk', 'base_automation', 'portal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/crm_service_data.xml',
        'data/res_partner_data.xml',
        'data/signature_item_type_data.xml',
        'data/helpdesk_demo.xml',
        'data/ticket_type_activity_data.xml',
#         'data/stage_activity_data.xml',
        'data/crm_demo.xml',
        'data/ticket_type_activity_data.xml',
#         'data/base_automation_demo.xml',
        'data/sales_team_demo.xml',
        'views/crm_views.xml',
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
    ],
    'qweb': ['static/src/xml/*.xml'],
}
