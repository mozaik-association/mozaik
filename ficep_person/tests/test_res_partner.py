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


class test_res_partner(SharedSetupTransactionCase):

    _data_files = ('data/person_data.xml',
                  )

    _module_ns = 'ficep_person'

    def setUp(self):
        super(test_res_partner, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.partner_model = self.registry('res.partner')

        self.partner_fgtb_id = self.ref('%s.res_partner_fgtb' % self._module_ns)
        self.partner_marc_id = self.ref('%s.res_partner_marc' % self._module_ns)

        self.context = {}

    def test_res_partner_names(self):
        """
        ======================
        test_res_partner_names
        ======================
        Test the overiding of the name_get method to compute display_name
        """
        cr, uid, context = self.cr, self.uid, self.context
        fgtb_id, marc_id = self.partner_fgtb_id, self.partner_marc_id
        partner_model = self.partner_model

        # Check for reference data
        vals = partner_model.read(cr, uid, [fgtb_id], ['is_company'], context=context)[0]
        self.assertTrue(vals['is_company'], 'Wrong expected reference data for this test')
        vals = partner_model.read(cr, uid, [marc_id], ['is_company'], context=context)[0]
        self.assertFalse(vals['is_company'], 'Wrong expected reference data for this test')

        # Change name of a company
        self.partner_model.write(cr, uid, [fgtb_id], {'name': 'newname'}, context=context)
        vals = partner_model.read(cr, uid, [fgtb_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], 'newname', 'Update partner name fails with wrong name')
        self.assertEqual(vals['display_name'], 'newname', 'Update partner name fails with wrong display_name')

        # Change various names of a contact

        # 1/ firstname, lastname
        self.partner_model.write(cr, uid, [marc_id],
                                 {'firstname': 'first', 'lastname': 'last', 'usual_firstname': False, 'usual_lastname': False,}, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('last', 'first'), 'Update both partner first and last names fails with wrong name')
        self.assertEqual(vals['display_name'], vals['name'], 'Update both partner first and last names fails with wrong display_name')

        # 2/ usual_firstname
        self.partner_model.write(cr, uid, [marc_id],
                                 {'usual_firstname': 'ufirst'}, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('last', 'first'), 'Update partner usual_firstname fails with wrong name')
        self.assertEqual(vals['display_name'], '%s %s' % ('last', 'ufirst'), 'Update partner usual_firstname fails with wrong display_name')

        # 3/ usual_lastname
        self.partner_model.write(cr, uid, [marc_id],
                                 {'usual_firstname': False, 'usual_lastname': 'ulast'}, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('last', 'first'), 'Update partner usual_lastname fails with wrong name')
        self.assertEqual(vals['display_name'], '%s %s' % ('ulast', 'first'), 'Update partner usual_lastname fails with wrong display_name')

        # 4/ all
        self.partner_model.write(cr, uid, [marc_id],
                                 {'firstname': 'Ian', 'lastname': 'FLEMING', 'usual_firstname': 'James', 'usual_lastname': 'BOND',}, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('FLEMING', 'Ian'), 'Update all partner names fails with wrong name')
        self.assertEqual(vals['display_name'], '%s %s' % ('BOND', 'James'), 'Update all partner names fails with wrong display_name')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
