# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Address',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_coordinate',
    ],
    'description': """
MOZAIK Address
==============
This module manages postal addresses and postal coordinates.
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/address_security.xml',
        'data/address_address_data.xml',
        'address_address_view.xml',
        'views/address_local_zip_view.xml',
        'address_local_street_view.xml',
        'coordinate_category_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_address.xml',
        'wizard/allow_duplicate_view.xml',
        'wizard/bounce_editor_view.xml',
        'wizard/change_co_residency_address.xml',
        'wizard/print_postal_from_partner_wizard_view.xml',
        'reports/report_res_partner_postal_coordinate_label_view.xml',
        'reports/report_postal_coordinate_label_view.xml',
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
