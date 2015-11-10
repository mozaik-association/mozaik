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

import logging

from anybox.testing.openerp import SharedSetupTransactionCase

_logger = logging.getLogger(__name__)


class test_membership_request(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/communication_data.xml',
    )

    _module_ns = 'mozaik_communication'

    def setUp(self):
        super(test_membership_request, self).setUp()
        self.test_distribution_list_id = self.ref(
            '%s.distribution_list_newsletter' % self._module_ns)
        self.paul = self.browse_ref(
            '%s.res_partner_paul' % self._module_ns)

    def test_newsletter_request_unknown(self):
        mr_obj = self.env['membership.request']
        vals = {
            'lastname': 'Anonymous',
            'firstname': 'Anonymous',
            'state': 'confirm',
            'request_type': 'n',
            'distribution_list_id': self.test_distribution_list_id
        }
        vals = mr_obj.pre_process(vals)
        mr1 = mr_obj.create(vals)
        mr1.validate_request()
        self.env.invalidate_all()
        self.assertTrue(self.test_distribution_list_id
                        in mr1.partner_id.opt_in_ids.ids)

    def test_newsletter_from_opt_out_to_opt_in(self):
        mr_obj = self.env['membership.request']
        vals = {
            'lastname': self.paul.lastname,
            'firstname': self.paul.firstname,
            'state': 'confirm',
            'request_type': 'n',
            'distribution_list_id': self.test_distribution_list_id,
            'partner_id': self.paul.id,
        }
        vals = mr_obj.pre_process(vals)
        mr1 = mr_obj.create(vals)
        mr1.validate_request()
        self.env.invalidate_all()
        self.assertTrue(self.test_distribution_list_id
                        in mr1.partner_id.opt_in_ids.ids)
        self.assertTrue(self.test_distribution_list_id
                        not in mr1.partner_id.opt_out_ids.ids)
