# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_phone, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_phone is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_phone is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_phone.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Phone',
    'version': '1.0.1',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_coordinate',
    ],
    'description': """
MOZAIK Phone
============
This module manages phone numbers and phone coordinates.
It covers three types of phone: fix, mobile and fax.
Numbers are normalized regarding the external python library: phonenumbers
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/phone_security.xml',
        'data/ir_config_parameter_data.xml',
        'data/phone_phone_data.xml',
        'phone_phone_view.xml',
        'coordinate_category_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_phone.xml',
        'wizard/allow_duplicate_view.xml',
        'wizard/bounce_editor_view.xml',
        'wizard/change_phone_type.xml',
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
