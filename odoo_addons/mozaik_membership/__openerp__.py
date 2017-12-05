# -*- coding: utf-8 -*-
# Copyright 2017 Acsone Sa/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK: Membership',
    'version': '8.0.1.0.2',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'product',
        'mozaik_person',
        'mozaik_person_coordinate',
        'mozaik_structure',
    ],
    'description': """
MOZAIK Membership
=================
Add models
* Membership
* Membership History
* Membership Request
It defines a required m2o to Internal Instance on local zip.
It replicates this instance on partner which main address is related to this
local zip, default instance otherwise. This field is added to all views
(search, tree and form) of a partner.
""",
    'images': [
    ],
    'data': [
        'data/membership_state_data.xml',
        'data/abstract_coordinate_data.xml',
        'data/res_partner_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/product_data.xml',
        'data/ir_cron_membership.xml',
        'security/membership_security.xml',
        'security/ir.model.access.csv',
        'membership_workflow.xml',
        'product_view.xml',
        'membership_view.xml',
        'address_local_zip_view.xml',
        'coordinate_view.xml',
        'partner_involvement_view.xml',
        'partner_relation_view.xml',
        'mandate_view.xml',
        'wizard/change_main_address.xml',
        'wizard/force_int_instance.xml',
        'wizard/generate_reference.xml',
        'wizard/pass_former_member.xml',
        'report/waiting_member_report_view.xml',
        'views/structure_view.xml',
        'views/membership_request_view.xml',
        'views/res_partner_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
