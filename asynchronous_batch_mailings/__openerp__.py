# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of asynchronous_batch_mailings, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     asynchronous_batch_mailings is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     asynchronous_batch_mailings is distributed in the hope
#     that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with asynchronous_batch_mailings.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Asynchronous Batch Mailings',
    'version': '1.0',
    'author': 'ACSONE SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'category': 'Marketing',
    'depends': [
        'mail',
        'connector',
    ],
    'description': """
Asynchronous Batch Mailings
===========================
This module allows to send emails by an asynchronous way.
Moreover it provides a way to split huge mailing.
Two parameters are available:
* the mailing size from which the mailing must become asynchronous
* the batch size
""",
    'images': [
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
