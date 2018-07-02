# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Sample Customization',
    'version': '11.0.1.0.0',
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
        '../mozaik_thesaurus/tests/data/thesaurus_data.xml',
        '../mozaik_structure/tests/data/structure_data.xml',
        '../mozaik_person/tests/data/res_partner_data.xml',
        '../mozaik_person/tests/data/partner_involvement_category_data.xml',
        '../mozaik_coordinate/tests/data/coordinate_category_data.xml',
        '../mozaik_email/tests/data/email_data.xml',
        '../mozaik_address/tests/data/reference_data.xml',
        '../mozaik_address/tests/data/address_data.xml',
        '../mozaik_phone/tests/data/phone_data.xml',
        '../mozaik_person_coordinate/tests/data/relation_data.xml',
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
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': False,
}
