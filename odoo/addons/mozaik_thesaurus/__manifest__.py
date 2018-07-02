# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Thesaurus',
    'version': '11.0.1.0.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'license': 'AGPL-3',
    'website': 'http://www.acsone.eu',
    'category': 'Political Association',
    'depends': [
        'mozaik_base',
    ],
    'description': """
MOZAIK Thesaurus
================
Implements a light thesaurus for indexation purpose.
Model is read-only for all users except thesaurus managers that are followers
of all terms.
Creating a new term will send a message to all this followers requesting
their validation.
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/thesaurus_data.xml',
        'views/thesaurus_view.xml',
        'wizard/thesaurus_terms_loader_view.xml',
    ],
    'installable': False,
}
