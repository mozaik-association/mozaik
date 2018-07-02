# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Portal',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_membership',
    ],
    'description': """
MOZAIK Portal
=============
This module manage portal user features
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_security.xml',
        'res_partner_view.xml',
        'distribution_list_view.xml',
        'event_view.xml',
        'portal_view.xml',
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
