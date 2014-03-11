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


class test_coordinate_wizard(object):
    #unittest2 run test for the abstract class too
    #resolved with a dual inherit on the abstract and the common.NAME

    def setUp(self):
        super(test_coordinate_wizard, self).setUp()

        self.model_partner = self.registry('res.partner')

        self.partner_id_1 = self.ref('%s.res_partner_marc' % self._module_ns)
        self.partner_id_2 = self.ref('%s.res_partner_thierry' % self._module_ns)
        self.partner_id_3 = self.ref('%s.res_partner_jacques' % self._module_ns)

        self.model_coordinate_wizard = None
        self.model_coordinate = None
        self.model_id_1 = None
        self.coo_into_partner = None
        self.model_coordinate_id_1 = None
        self.model_coordinate_id_2 = None

    def change_main_coordinate(self, invalidate):
        """
        ========================
        change_main_coordinate
        ========================
        :param invalidate: value for ``invalidate_previous_model_coordinate``
        :type invalidate: boolean
        :rparam: id or [ids]
        :rtype: integer
        """
        context = {
            'active_ids': [self.partner_id_1, self.partner_id_2, self.partner_id_3],
            'target_model': self.model_coordinate._name,
        }
        wiz_vals = {
            self.model_coordinate._discriminant_field: self.model_id_1,
            'invalidate_previous_coordinate': invalidate,
        }
        wiz_id = self.model_coordinate_wizard.create(self.cr, self.uid, wiz_vals, context=context)
        return self.model_coordinate_wizard.button_change_main_coordinate(self.cr, self.uid, [wiz_id], context=context)

    def test_mass_replication(self):
        """
        =====================
        test_mass_replication
        =====================
        This test check the fact that the created model coordinate are the main
        for their associated partner.

        Assure that the model_id_N is well replicated into the partner form:
            partner_N.mobile_coordinate.model_id.id = self.model_id_N
        Assure that the model replicated is main:
            partner_N.mobile_coordinate.is_main = True
        If those condition are well respected then replication is functional
        """
        self.change_main_coordinate(True)
        model_coo = self.model_partner.read(self.cr,
                                            self.uid, [self.partner_id_1,
                                            self.partner_id_2,
                                            self.partner_id_3], [self.coo_into_partner], context={})
        for model_coordinate_vals in model_coo:
            c_rec = self.model_coordinate.browse(self.cr, self.uid, model_coordinate_vals['mobile_coordinate_id'][0], context={})
            self.assertEqual(c_rec[self.model_coordinate._discriminant_field].id == self.model_id_1 and
                             c_rec.is_main == True, True, 'model Coordinate Should Be Replicate Into The  Associated Partner')

    def test_mass_replication_with_invalidate(self):
        """
        =====================================
        test_mass_replication_with_invalidate
        =====================================
        This test check the fact that the ``mass_select_as_main`` of
        the wizard will right invalidate the previous model coordinate if it is
        wanted
        Check also the fact that if a selected partner has already the new selected number
        into a model coordinate then it will not be invalidate
        **Note**
        Context:
        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- main_model_coo2 ------ model 2 : active
        u2 ----- model_coo_3 ---------- model 1 : active
        Excepted Result:

        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- model_coo2      ------ model 2 : not active
        u2 ----- main_model_coo_3------ model 1 : active
        """
        self.change_main_coordinate(True)
        active = self.model_coordinate.read(self.cr,
                                                  self.uid,
                                                  [self.model_coordinate_id_1, self.model_coordinate_id_2],
                                                  ['active'],
                                                  context={})
        self.assertEqual(active[0]['active'], True, 'Should not invalidate a model coordinate that is already the \
                                                     main for the selected partner with this selected number')
        self.assertEqual(active[1]['active'], False, 'Previous model Coordinate should be invalidate')

    def test_mass_replication_without_invalidate(self):
        """
        ========================================
        test_mass_replication_without_invalidate
        ========================================
        This test check the fact that the ``mass_select_as_main`` of
        the wizard doesn't invalidate the previous model coordinate if it is
        not wanted
        **Note**
        Context:

        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- main_model_coo2 ------ model 2 : active
        u2 ----- model_coo_3 ---------- model 1 : active
        Excepted Result:

        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- model_coo2      ------ model 2 : active
        u2 ----- main_model_coo_3------ model 1 : active
        """
        self.change_main_coordinate(False)
        active = self.model_coordinate.read(self.cr,
                                                  self.uid,
                                                  self.model_coordinate_id_2,
                                                  ['active'],
                                                  context={})['active']
        self.assertEqual(active, True, 'Previous model Coordinate should not be invalidate')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
