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
    'name': 'MOZAIK: Chart of account',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Localization/Account Charts',
    'depends': [
        'ficep_retrocession',
        'ficep_membership',
    ],
    'description': """
l10n MOZAIK
===========
This is the base module to manage the generic accounting chart for the application
    """,
    'images': [
    ],
    'data': [
        'data/account_template.xml',
        'data/account_chart_template.xml',
        'data/account_installer.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'sequence': 150,
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
