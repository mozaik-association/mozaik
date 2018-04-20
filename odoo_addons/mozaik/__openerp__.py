# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK',
    'version': '8.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_help',
        'mozaik_mobile',
        'mozaik_portal',
        'mozaik_person',
        'mozaik_involvement_followup',
        'mozaik_chart_account',
        'mozaik_retrocession',
        'mozaik_account',
        'mozaik_communication',
        'connector_support',
    ],
    'description': """
MOZAIK
======
Loads all applicative modules
""",
    'images': [
    ],
    'data': [
        'security/security.xml',
        'data/res_users_data.xml',
        'views/mail_followers.xml',
    ],
    'qweb': [
    ],
    'demo': [
        'demo/res_users_demo.xml',
    ],
    'license': 'AGPL-3',
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
