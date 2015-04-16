# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Membership',
    'version': '1.0.2',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_account',
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
        'security/membership_security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter_data.xml',
        'data/product_data.xml',
        'data/ir_cron_membership.xml',
        'membership_workflow.xml',
        'product_view.xml',
        'membership_request_view.xml',
        'membership_view.xml',
        'address_local_zip_view.xml',
        'res_partner_view.xml',
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
