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
    'name': 'FICEP: Retrocession',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'ficep_structure',
        'ficep_mandate',
        'ficep_membership',
        'ficep_account',
    ],
    'description': """
FICEP Retrocession
==================
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ficep_retrocession_security.xml',
        'mandate_actions.xml',
        'structure_view.xml',
        'retrocession_view.xml',
        'mandate_view.xml',
        'wizard/retrocession_factory_wizard.xml',
        'wizard/report_retrocession_wizard.xml',
        'reports/report_payment_request_view.xml',
        'reports/report_payment_certificate_view.xml',
        'data/email_template_data.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
