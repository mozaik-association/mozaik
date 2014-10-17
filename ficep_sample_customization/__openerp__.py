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
    'name': 'MOZAIK: Sample Customization',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik',
    ],
    'description': """
MOZAIK Sample Customization
===========================
    """,
    'images': [
    ],
    'data': [
        # first other data ...
        '../mozaik_base/tests/data/res_partner_data.xml',
        '../mozaik_base/tests/data/res_users_data.xml',
        '../mozaik_structure/tests/data/structure_data.xml',
        '../mozaik_person/tests/data/res_partner_data.xml',
        '../mozaik_coordinate/tests/data/coordinate_category_data.xml',
        '../mozaik_email/tests/data/email_data.xml',
        '../mozaik_address/tests/data/reference_data.xml',
        '../mozaik_address/tests/data/address_data.xml',
        '../mozaik_phone/tests/data/phone_data.xml',
        '../mozaik_person_coordinate/tests/data/relation_data.xml',
        '../mozaik_thesaurus/tests/data/thesaurus_data.xml',
        '../mozaik_membership/tests/data/structure_address_data.xml',
        '../mozaik_mandate/tests/data/mandate_data.xml',
        '../mozaik_retrocession/tests/data/retrocession_data.xml',
        '../mozaik_membership/tests/data/membership_request_data.xml',
        '../mozaik_communication/tests/data/communication_data.xml',
        '../mozaik_communication/tests/data/postal_mail_data.xml',
        # ... and finally ...
        'demo/company_demo.xml',
        'demo/users_demo.xml',
        'demo/sample_customization_demo.xml',
        'demo/res_lang_install.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
