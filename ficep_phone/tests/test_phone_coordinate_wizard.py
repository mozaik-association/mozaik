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
import openerp.tests.common as common
import logging

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_phone_coordinate_wizard(common.TransactionCase):

    def setUp(self):
        super(test_phone_coordinate_wizard, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        cr, uid = self.cr, self.uid
        self.phone_coordinate_wizard = self.registry('phone.coordinate.wizard')
        self.model_partner = self.registry('res.partner')
        self.model_phone = self.registry('phone.phone')
        self.model_phone_coordinate = self.registry('phone.coordinate')

        self.partner_id_1 = self.model_partner.create(cr, uid, {'name': 'partner_1'}, context={})
        self.partner_id_2 = self.model_partner.create(cr, uid, {'name': 'partner_2'}, context={})
        self.partner_id_3 = self.model_partner.create(cr, uid, {'name': 'partner_3'}, context={})

        self.phone_id_1 = self.model_phone.create(cr, uid, {'name': '+32 478 85 25 25',
                                                                   'type': 'mobile'
                                                                   }, context={})
        self.phone_id_2 = self.model_phone.create(cr, uid, {'name': '+32 465 00 00 00',
                                                                   'type': 'mobile'
                                                                   }, context={})

        self.phone_coordinate_id_1 = self.model_phone_coordinate.create(cr, uid, {'phone_id': self.phone_id_1,
                                                                                 'partner_id': self.partner_id_1,
                                                                                 'is_main': True,
                                                                                   }, context={})
        self.phone_coordinate_id_2 = self.model_phone_coordinate.create(cr, uid, {'phone_id': self.phone_id_2,
                                                                                   'partner_id': self.partner_id_2,
                                                                                   'is_main': True,
                                                                                   }, context={})
        self.phone_coordinate_id_3 = self.model_phone_coordinate.create(cr, uid, {'phone_id': self.phone_id_1,
                                                                                 'partner_id': self.partner_id_2,
                                                                                 'is_main': False,
                                                                                   }, context={})

    def mass_select_as_main(self, invalidate):
        """
        ===================
        mass_select_as_main
        ===================
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
        return self.phone_coordinate_wizard.mass_select_as_main(self.cr, self.uid, [wiz_id], context=context)

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
        self.mass_select_as_main(True)
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
        ========================================
        test_mass_replication_with_invalidate
        ========================================
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
        self.mass_select_as_main(True)
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
        self.mass_select_as_main(False)
        active = self.model_phone_coordinate.read(self.cr,
                                                  self.uid,
                                                  self.phone_coordinate_id_2,
                                                  ['active'],
                                                  context={})['active']
        self.assertEqual(active, True, 'Previous Phone Coordinate should not be invalidate')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
