# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Email',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_coordinate',
    ],
    'description': """
MOZAIK Email
============
This module manages email coordinates.
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/email_security.xml',
        'email_coordinate_view.xml',
        'coordinate_category_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_email.xml',
        'wizard/allow_duplicate_view.xml',
        'wizard/bounce_editor_view.xml',
        'wizard/export_vcard_view.xml',
        'data/email_data.xml',
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
