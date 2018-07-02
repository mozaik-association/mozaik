# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Online Help',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_base',
        'help_online',
    ],
    'description': """
MOZAIK Online Help
==================
* Provide a full online help feature for the application
""",
    'images': [
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
        'data/help_auto_backup.xml',
        'data/help_online_data.xml',
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
