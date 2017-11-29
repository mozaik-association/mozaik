# -*- coding: utf-8 -*-
# Copyright 2017 Acsone Sa/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'MOZAIK: Person',
    'version': '8.0.1.0.1',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'base_suspend_security',
        'mozaik_duplicate',
        'mozaik_thesaurus',
        'mozaik_partner_assembly',
    ],
    'description': """
MOZAIK Person
=============
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/person_security.xml',
        'data/res_partner_sequence_data.xml',
        'views/partner_involvement_view.xml',
        'res_partner_view.xml',
        'person_view.xml',
        'wizard/create_user_from_partner_view.xml',
        'wizard/allow_duplicate_view.xml',
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
