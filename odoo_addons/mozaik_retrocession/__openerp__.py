# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_retrocession, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_retrocession is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_retrocession is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_retrocession.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Retrocession',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_structure',
        'mozaik_mandate',
        'mozaik_membership',
        'mozaik_account',
    ],
    'description': """
MOZAIK Retrocession
===================
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/retrocession_security.xml',
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
    'license': 'AGPL-3',
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
