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
from anybox.testing.openerp import SharedSetupTransactionCase
import logging
_logger = logging.getLogger(__name__)


class test_phone_coordinate_wizard(SharedSetupTransactionCase):

    _data_files = ('../../ficep_person/tests/data/person_data.xml',
                   'data/phone_data.xml',
                  )

    _module_ns = 'ficep_phone'

    def setUp(self):
        super(test_phone_coordinate_wizard, self).setUp()

        self.phone_coordinate_wizard = self.registry('phone.change.main.number')
        self.model_partner = self.registry('res.partner')
        self.model_phone_coordinate = self.registry('phone.coordinate')

        self.partner_id_1 = self.ref('%s.res_partner_marc' % self._module_ns)
        self.partner_id_2 = self.ref('%s.res_partner_thierry' % self._module_ns)
        self.partner_id_3 = self.ref('%s.res__partner_sophie' % self._module_ns)

        self.phone_id_1 = self.ref('%s.mobile_one' % self._module_ns)

        self.phone_coordinate_id_1 = self.ref('%s.main_mobile_coordinate_one' % self._module_ns)
        self.phone_coordinate_id_2 = self.ref('%s.main_mobile_coordinate_two' % self._module_ns)

    def change_main_coordinate(self, invalidate):
        """
        ========================
        change_main_coordinate
        ========================
        :param invalidate: value for ``invalidate_previous_phone_coordinate``
        :type invalidate: boolean
        :rparam: id or [ids]
        :rtype: integer
        """
        context = {
            'active_ids': [self.partner_id_1, self.partner_id_2, self.partner_id_3]
        }
        wiz_vals = {
            'phone_id': self.phone_id_1,
            'invalidate_previous_phone_coordinate': invalidate,
        }
        wiz_id = self.phone_coordinate_wizard.create(self.cr, self.uid, wiz_vals, context=context)
        return self.phone_coordinate_wizard.change_main_phone_number(self.cr, self.uid, [wiz_id], context=context)

    def test_mass_replication(self):
        """
        =====================
        test_mass_replication
        =====================
        This test check the fact that the created phone coordinate are the main
        for their associated partner.

        Assure that the phone_id_N is well replicated into the partner form:
            partner_N.mobile_coordinate.phone_id.id = self.phone_id_N
        Assure that the phone replicated is main:
            partner_N.mobile_coordinate.is_main = True
        If those condition are well respected then replication is functional
        """
        self.change_main_coordinate(True)
        phone_coo = self.model_partner.read(self.cr,
                                            self.uid, [self.partner_id_1,
                                            self.partner_id_2,
                                            self.partner_id_3], ['mobile_coordinate_id'], context={})
        for phone_coordinate_vals in phone_coo:
            pc_rec = self.model_phone_coordinate.browse(self.cr, self.uid, phone_coordinate_vals['mobile_coordinate_id'][0], context={})
            self.assertEqual(pc_rec.phone_id.id == self.phone_id_1 and
                             pc_rec.is_main == True, True, 'Phone Coordinate Should Be Replicate Into The  Associated Partner')

    def test_mass_replication_with_invalidate(self):
        """
        =====================================
        test_mass_replication_with_invalidate
        =====================================
        This test check the fact that the ``mass_select_as_main`` of
        the wizard will right invalidate the previous phone coordinate if it is
        wanted
        Check also the fact that if a selected partner has already the new selected number
        into a phone coordinate then it will not be invalidate
        **Note**
        Context:
        u1 ----- main_phone_coo1 ------ phone 1 : active
        u2 ----- main_phone_coo2 ------ phone 2 : active
        u2 ----- phone_coo_3 ---------- phone 1 : active
        Excepted Result:

        u1 ----- main_phone_coo1 ------ phone 1 : active
        u2 ----- phone_coo2      ------ phone 2 : not active
        u2 ----- main_phone_coo_3------ phone 1 : active
        """
        self.change_main_coordinate(True)
        active = self.model_phone_coordinate.read(self.cr,
                                                  self.uid,
                                                  [self.phone_coordinate_id_1, self.phone_coordinate_id_2],
                                                  ['active'],
                                                  context={})
        self.assertEqual(active[0]['active'], True, 'Should not invalidate a phone coordinate that is already the \
                                                     main for the selected partner with this selected number')
        self.assertEqual(active[1]['active'], False, 'Previous Phone Coordinate should be invalidate')

    def test_mass_replication_without_invalidate(self):
        """
        ========================================
        test_mass_replication_without_invalidate
        ========================================
        This test check the fact that the ``mass_select_as_main`` of
        the wizard doesn't invalidate the previous phone coordinate if it is
        not wanted
        **Note**
        Context:

        u1 ----- main_phone_coo1 ------ phone 1 : active
        u2 ----- main_phone_coo2 ------ phone 2 : active
        u2 ----- phone_coo_3 ---------- phone 1 : active
        Excepted Result:

        u1 ----- main_phone_coo1 ------ phone 1 : active
        u2 ----- phone_coo2      ------ phone 2 : active
        u2 ----- main_phone_coo_3------ phone 1 : active
        """
        self.change_main_coordinate(False)
        active = self.model_phone_coordinate.read(self.cr,
                                                  self.uid,
                                                  self.phone_coordinate_id_2,
                                                  ['active'],
                                                  context={})['active']
        self.assertEqual(active, True, 'Previous Phone Coordinate should not be invalidate')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
