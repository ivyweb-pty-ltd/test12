# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal

CustomerPortal.OPTIONAL_BILLING_FIELDS = CustomerPortal.OPTIONAL_BILLING_FIELDS + ['id_type', 'id_rsa', 'mobile']

# TODO: if id_type == res_id than call onchagne of id_type and set date of birth, gender l
# look at onchange res_id on part + error handling
