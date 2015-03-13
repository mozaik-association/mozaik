# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Person - Coordinate',
    'version': '1.0',
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
    'sequence': 150,
    'auto_install': True,  # automatically install if all depends loaded
    'installable': True,
}
