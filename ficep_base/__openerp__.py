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
    'name': 'FICEP: Base',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'base',
        'document',
        'mass_mailing',
        'product',
        #'event',
        'partner_firstname',     # from https://github.com/OCA/partner-contact
        #'mass_editing',          # from https://github.com/OCA/server-tools/7.0
        'cron_run_manually',     # from https://github.com/OCA/server-tools/7.0
        'auth_admin_passkey',    # from https://github.com/OCA/server-tools/7.0
        'settings_improvement',  # from https://github.com/acsone/acsone-addons
        'distribution_list',     # from https://github.com/acsone/acsone-addons
        'readonly_bypass',       # from https://github.com/acsone/acsone-addons
        'help_online',           # from https://github.com/acsone/acsone-addons
        'connector',             # from https://github.com/OCA/connector

        # to speed test without testing standard addons from a pre-loaded squeleton database:
        'analytic',
        'board',
        'edi',
        # load manually in this database ficep_base and the following modules:
        #'membership',        # close manually wizard without loading any charts templates
        #'account_accountant',
        #'account_cancel',
    ],
    'description': """
FICEP Base
==========
* improve user context adding a flag by ficep group
* provide a work-around to handle correctly the readonly attribute of the widget mail_thread
* define ficep menus skeleton
    """,
    'images': [
    ],
    'data': [
        'data/delete_data.xml',
        'security/ficep_base_security.xml',
        'security/ir.model.access.csv',
        'data/ir_filters_data.xml',
        'data/res_lang_data.xml',
        'data/res_lang_install.xml',
        'data/ir_config_parameter_data.xml',
        'data/product_data.xml',
        'ficep_view.xml',
        'res_partner_view.xml',
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

