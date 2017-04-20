# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_sample_customization, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_sample_customization is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_sample_customization is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_sample_customization.
#     If not, see <http://www.gnu.org/licenses/>.
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
        '../mozaik_membership/tests/data/membership_request_data.xml',
        '../mozaik_membership/tests/data/res_partner_data.xml',
        '../mozaik_mandate/tests/data/mandate_data.xml',
        '../mozaik_retrocession/tests/data/retrocession_data.xml',
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
    'license': 'AGPL-3',
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
