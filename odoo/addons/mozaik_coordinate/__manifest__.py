# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Coordinate',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_duplicate',
    ],
    'description': """
MOZAIK Coordinate
=================
* Manage categories of email, phone and postal coordinates: private,
  professional, ...
* provide an abstract model (and related wizard) for all kinds of coordinates
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'coordinate_category_view.xml',
        'abstract_coordinate_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_coordinate.xml',
        'wizard/bounce_editor_view.xml',
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
