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
from uuid import uuid4
from anybox.testing.openerp import SharedSetupTransactionCase


class test_force_int_instance(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../ficep_base/tests/data/res_partner_data.xml',
        # load structures
        '../../ficep_structure/tests/data/structure_data.xml',
    )

    _module_ns = 'ficep_membership'

    def setUp(self):
        super(test_force_int_instance, self).setUp()
        self.partner_obj = self.registry['res.partner']
        self.int_instance_obj = self.registry['int.instance']

    def test_force_int_instance_action(self):
        """
        Check that int_instance is well updated after process a
        `force_int_instance_action`
        """
        cr, uid, context = self.cr, self.uid, {}
        wiz_obj = self.registry['force.int.instance']

        vals = {
            'lastname': '%s' % uuid4(),
        }

        partner_id = self.partner_obj.create(cr, uid, vals, context=context)
        int_instance_id = self.ref('%s.int_instance_04' % self._module_ns)

        vals = {
            'partner_id': partner_id,
            'int_instance_id': int_instance_id,
        }
        wiz_id = wiz_obj.create(
            cr, uid, vals, context=context)
        wiz_obj.force_int_instance_action(cr, uid, [wiz_id], context=context)

        updated_int_instance_id = self.partner_obj.read(
            cr, uid, partner_id, ['int_instance_id'],
            context=context)['int_instance_id'][0]
        self.assertEqual(int_instance_id, updated_int_instance_id,
                         'Instance should be updated with forced value')
