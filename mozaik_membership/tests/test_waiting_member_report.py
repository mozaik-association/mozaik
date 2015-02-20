# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import date, timedelta
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.addons.mozaik_membership.report.\
    waiting_member_report import DEFAULT_NB_DAYS


class test_membership(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../mozaik_base/tests/data/res_partner_data.xml',
        # load structures
        '../../mozaik_structure/tests/data/structure_data.xml',
        # load address of this partner
        '../../mozaik_address/tests/data/reference_data.xml',
        # load postal_coordinate of this partner
        '../../mozaik_address/tests/data/address_data.xml',
        # load phone_coordinate of this partner
        '../../mozaik_phone/tests/data/phone_data.xml',
        # load terms and requests
        '../../mozaik_thesaurus/tests/data/thesaurus_data.xml',
        'data/membership_request_data.xml',
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_membership, self).setUp()
        self.partner_obj = self.registry['res.partner']

        self.icp = self.registry('ir.config_parameter')
        self.msr = self.registry('membership.request')
        self.wmr = self.registry('waiting.member.report')

        self.pauline = self.browse_ref(
            '%s.res_partner_pauline' % self._module_ns)

        self.member_request = self.browse_ref(
            '%s.membership_request_mp' % self._module_ns)

    def test_process_accept_members(self):
        """
        Test that `waiting.member.report` will correctly make pass the partner
        into member after a defined number of days (`ir.parameter`)
            * Validate this membership
            * Check that `ir.config_parameter` key `nb_days` exists
            * `date_from` (membership line of Pauline)
              = today - (parameter value - 5)
            * launch `process_accept_members` and check that Pauline is not
              a `member`
            * Update parameter value with string value 'blabla'
            * Import DEFAULT_NB_DAYS
            * `date_from` (membership line of Pauline)
              = today - (DEFAULT_NB_DAYS + 5)
            * launch `process_accept_members` and check that Pauline now
              `member`
        """
        def update_memberlines_date_from(member_lines, new_date_from):
            for member_line in member_lines:
                member_line.write({'date_from': new_date_from})

        cr, uid, context = self.cr, self.uid, {'hide_nb_days_warning': True}
        msr_ids = [self.member_request.id]
        self.msr.validate_request(cr, uid, msr_ids, context=context)
        self.pauline.signal_workflow('paid')
        icp_ids = self.icp.search(
            cr, uid, [('key', '=', 'nb_days')], context=context)
        self.assertTrue(icp_ids, 'Should have a parameter nb_days.')

        icp_rec = self.icp.browse(cr, uid, icp_ids, context=context)[0]
        to_substract = int(icp_rec.value) - 5
        new_date_from = date.today() - timedelta(days=to_substract)
        update_memberlines_date_from(self.pauline.membership_line_ids,
                                     new_date_from)
        self.wmr.process_accept_members(cr, uid)
        self.pauline = self.partner_obj.browse(cr, uid, self.pauline.id,
                                               context=context)
        self.assertTrue(self.pauline.membership_state_id.code != 'member',
                        'Should not be a member: nb_days is not '
                        'greater than value of parameter')

        icp_rec.write({'value': 'blabla'})
        to_substract = DEFAULT_NB_DAYS + 5
        new_date_from = date.today() - timedelta(days=to_substract)
        update_memberlines_date_from(self.pauline.membership_line_ids,
                                     new_date_from)
        self.wmr.process_accept_members(cr, uid, context=context)
        self.pauline = self.partner_obj.browse(cr, uid, self.pauline.id,
                                               context=context)
        self.assertTrue(self.pauline.membership_state_id.code == 'member',
                        'Should not be a member: '
                        'nb_days is greater than DEFAULT_NB_DAYS')
