# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Person - Coordinate',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_person',
        'mozaik_email',
        'mozaik_address',
        'mozaik_phone',
    ],
    'description': """
MOZAIK Person - Coordinate
==========================
* Colors tree view.
* Add Relation Model For Partner
** Persons/Relations/Subject Relations
** Persons/Relations/Object Relations
** Persons/Configuration/Relation Category
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_duplicate.xml',
        'report/duplicates_analysis_report_view.xml',
        'partner_relation_view.xml',
        'res_partner_view.xml',
    ],
    'license': 'AGPL-3',
    'auto_install': True,
    'installable': False,
}
