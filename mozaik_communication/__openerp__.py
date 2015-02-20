# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Communication',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mass_mailing_distribution_list',
        'mozaik_membership',
        'mozaik_retrocession',
    ],
    'description': """
MOZAIK Communication
====================
* New Menus:
** Communication/Persons
** Communication/Mailing
** Communication/Postal Mailing
** Communication/Configuration
* Customization of the Distribution List Module
""",
    'images': [
        'static/src/img/icon-mass.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/communication_security.xml',
        'wizard/distribution_list_mass_function_view.xml',
        'wizard/add_registrations_view.xml',
        'wizard/distribution_list_add_filter_view.xml',
        'distribution_list_view.xml',
        'postal_mail_view.xml',
        'res_partner_view.xml',
        'communication_view.xml',
        'virtual_models_view.xml',
        'mass_mailing_view.xml',
        'email_template_view.xml',
        'event_view.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'sequence': 150,
    'installable': True,
    'auto_install': False,
}
