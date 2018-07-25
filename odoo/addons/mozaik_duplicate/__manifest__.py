# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mozaik: Duplicate',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_base',
        'mozaik_abstract_model',
    ],
    'description': """
MOZAIK Duplicate
================
* Provide an abstract model (and related wizard) to detect, repair and allow
  duplicates
""",
    'data': [
        'wizard/allow_duplicate_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
