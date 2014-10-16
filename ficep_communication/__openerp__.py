# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        'ficep_membership',
        'ficep_retrocession',
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
        'data/distribution_list_data.xml',
        'wizard/distribution_list_mass_function_view.xml',
        'wizard/add_registrations_view.xml',
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
    'sequence': 150,
    'installable': True,
    'auto_install': False,
}
