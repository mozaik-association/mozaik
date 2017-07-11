# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_address, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_address is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_address is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_address.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Address',
    'version': '8.0.1.0.1',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_coordinate',
    ],
    'description': """
MOZAIK Address
==============
This module manages postal addresses and postal coordinates.
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/address_security.xml',
        'data/address_address_data.xml',
        'address_address_view.xml',
        'address_local_zip_view.xml',
        'address_local_street_view.xml',
        'coordinate_category_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_address.xml',
        'wizard/allow_duplicate_view.xml',
        'wizard/bounce_editor_view.xml',
        'wizard/change_co_residency_address.xml',
        'wizard/print_postal_from_partner_wizard_view.xml',
        'reports/report_res_partner_postal_coordinate_label_view.xml',
        'reports/report_postal_coordinate_label_view.xml',
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
