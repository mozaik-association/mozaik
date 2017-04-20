# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Base',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'base',
        'portal',
        'document',
        'product',
        # from https://github.com/acsone/acsone-addons
        'asynchronous_batch_mailings',
        'asynchronous_batch_mailings_unique_campaign',
        'mass_mailing_distribution_list',
        'event_mass_mailing',
        'settings_improvement',
        'readonly_bypass',
        'html_widget_embedded_picture',
        # from https://github.com/OCA/partner-contact
        'partner_firstname',
        # from https://github.com/OCA/server-tools
        'cron_run_manually',
        'auth_admin_passkey',
        # from https://github.com/OCA/web
        'help_online',
        'incoming_mail_embedded_picture_reader',
    ],
    'description': """
MOZAIK Base
===========
* improve user context adding a flag by Mozaik group
* provide a work-around to handle correctly the readonly attribute of the
widget mail_thread
* define Mozaik menus skeleton
""",
    'images': [
    ],
    'data': [
        'data/delete_data.xml',
        'data/base_data.xml',
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'data/ir_filters_data.xml',
        'data/res_lang_data.xml',
        'data/ir_config_parameter_data.xml',
        'base_view.xml',
        'res_partner_view.xml',
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
    'application': False,
}
