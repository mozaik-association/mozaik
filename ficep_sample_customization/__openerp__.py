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
    'name': 'FICEP: Sample Customization',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'ficep',
        'l10n_ficep',
    ],
    'description': """
FICEP Sample Customization
==========================
    """,
    'images': [
    ],
    'data': [
         '../ficep_account/tests/data/account_installer.xml',
         'demo/company_demo.xml',
         'demo/users_demo.xml',
         '../ficep_base/tests/data/res_partner_data.xml',
         '../ficep_base/tests/data/res_users_data.xml',
         '../ficep_structure/tests/data/structure_data.xml',
         '../ficep_person/tests/data/res_partner_data.xml',
         '../ficep_person/tests/data/partner_involvment_data.xml',
         '../ficep_coordinate/tests/data/coordinate_category_data.xml',
         '../ficep_email/tests/data/email_data.xml',
         '../ficep_address/tests/data/reference_data.xml',
         '../ficep_address/tests/data/address_data.xml',
         '../ficep_phone/tests/data/phone_data.xml',
         '../ficep_person_coordinate/tests/data/relation_data.xml',
         '../ficep_thesaurus/tests/data/thesaurus_data.xml',
         '../ficep_membership/tests/data/structure_address_data.xml',
         '../ficep_mandate/tests/data/mandate_data.xml',
         '../ficep_communication/tests/data/communication_data.xml',
         '../ficep_retrocession/tests/data/retrocession_data.xml',
         '../ficep_membership/tests/data/membership_request_data.xml',
         'demo/sample_customization_demo.xml',  # must be the last
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
