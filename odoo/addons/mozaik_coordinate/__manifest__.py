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
        'mozaik_abstract_model',
        'mozaik_duplicate',
        'contacts',
    ],
    'description': """
MOZAIK Coordinate
=================
* Manage categories of email, phone and postal coordinates: private,
  professional, ...
* provide an abstract model (and related wizard) for all kinds of coordinates
""",
    'data': [
        'views/res_partner.xml',
        'views/abstract_coordinate.xml',
        'views/coordinate_category.xml',
        'security/ir.model.access.csv',
        'wizards/failure_editor.xml',
        'wizards/change_main_coordinate.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
