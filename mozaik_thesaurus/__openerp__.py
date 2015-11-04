# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_thesaurus, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_thesaurus is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_thesaurus is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_thesaurus.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Thesaurus',
    'version': '1.0.1',
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
    'sequence': 150,
    'installable': True,
    'auto_install': False,
}
