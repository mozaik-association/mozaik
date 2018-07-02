# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Mobile',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_communication',
    ],
    'description': """
MOZAIK Mobile
=============
* Provide mobile render to access partners
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/mobile_security.xml',
        'static/src/xml/mobile_view.xml',
        'views/mobile_templates.xml',
        'mobile_view.xml',
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
