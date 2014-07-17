# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'FICEP: Membership',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'ficep_account',
        'ficep_person_coordinate',
        'ficep_structure',
        'membership',
    ],
    'description': """
FICEP Membership
================
Add models
* Membership
* Membership History
* Membership Request
It defines a required m2o to Internal Instance on local zip.
It replicates this instance on partner which main address is related to this local zip,
default instance otherwise. This field is added to all views (search, tree and form) of a partner.

    """,
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/membership_security.xml',
        'membership_workflow.xml',
        'membership_view.xml',
        'membership_request_view.xml',
        'address_local_zip_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_address.xml',
        'data/ficep_membership_state_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/product_data.xml',
    ],
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
