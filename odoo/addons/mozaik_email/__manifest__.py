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
    'data': [
        'views/email_coordinate.xml',
        'views/coordinate_category.xml',
        'views/res_partner.xml',
        'wizards/change_main_email.xml',
        'wizards/allow_duplicate_wizard.xml',
        'wizards/failure_editor.xml',
        'security/abstract_coordinate.xml',
    ],
    'demo': [
        'demo/email_coordinate.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
