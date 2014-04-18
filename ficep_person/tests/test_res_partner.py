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
import logging
_logger = logging.getLogger(__name__)
from openerp.tools import SUPERUSER_ID
from openerp.osv import orm


class test_res_partner(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
    )

    _module_ns = 'ficep_person'

    def setUp(self):
        super(test_res_partner, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.partner_model = self.registry('res.partner')
        self.company_model = self.registry('res.company')
        self.user_model = self.registry('res.users')
        self.allow_duplicate_wizard_model = self.registry('allow.duplicate.wizard')

        self.partner_nouvelobs_id = self.ref('%s.res_partner_nouvelobs' % self._module_ns)
        self.partner_nouvelobs_bis_id = self.ref('%s.res_partner_nouvelobs_bis' % self._module_ns)
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

        # A/ Change various names of a company

        # 1/ name
        self.partner_model.write(cr, uid, [fgtb_id], {'name': 'newname', 'acronym': False}, context=context)
        vals = partner_model.read(cr, uid, [fgtb_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], 'newname', 'Update partner name fails with wrong name')
        self.assertEqual(vals['display_name'], vals['name'], 'Update partner name fails with wrong display_name')

        # 2/ acronym
        self.partner_model.write(cr, uid, [fgtb_id], {'acronym': 'abbrev'}, context=context)
        vals = partner_model.read(cr, uid, [fgtb_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], 'newname', 'Update partner name fails with wrong name')
        self.assertEqual(vals['display_name'], "%s (%s)" % (vals['name'], 'abbrev'), 'Update partner name fails with wrong display_name')

        # B/ Change various names of a contact

        # 1/ firstname, lastname
        self.partner_model.write(cr, uid, [marc_id],
                                 {'firstname': 'first', 'lastname': 'last', 'usual_firstname': False, 'usual_lastname': False, }, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('last', 'first'), 'Update both partner first and last names fails with wrong name')
        self.assertEqual(vals['display_name'], vals['name'], 'Update both partner first and last names fails with wrong display_name')

        # 2/ usual_firstname
        self.partner_model.write(cr, uid, [marc_id],
                                 {'usual_firstname': 'ufirst'}, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('last', 'first'), 'Update partner usual_firstname fails with wrong name')
        self.assertEqual(vals['display_name'], '%s %s (%s)' % ('last', 'ufirst', vals['name']), 'Update partner usual_firstname fails with wrong display_name')

        # 3/ usual_lastname
        self.partner_model.write(cr, uid, [marc_id],
                                 {'usual_firstname': False, 'usual_lastname': 'ulast'}, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('last', 'first'), 'Update partner usual_lastname fails with wrong name')
        self.assertEqual(vals['display_name'], '%s %s (%s)' % ('ulast', 'first', vals['name']), 'Update partner usual_lastname fails with wrong display_name')

        # 4/ all
        self.partner_model.write(cr, uid, [marc_id],
                                 {'firstname': 'Ian', 'lastname': 'FLEMING', 'usual_firstname': 'James', 'usual_lastname': 'BOND', }, context=context)
        vals = partner_model.read(cr, uid, [marc_id], ['name', 'display_name', 'printable_name'], context=context)[0]
        self.assertEqual(vals['name'], '%s %s' % ('FLEMING', 'Ian'), 'Update all partner names fails with wrong name')
        self.assertEqual(vals['display_name'], '%s %s (%s)' % ('BOND', 'James', vals['name']), 'Update all partner names fails with wrong display_name')
        self.assertEqual(vals['printable_name'], '%s %s' % ('James', 'BOND'), 'Update all partner names fails with wrong printable_name')

    def test_res_partner_duplicates(self):
        """
        ===========================
        test_res_partner_duplicates
        ===========================
        Test duplicate detection, permission and repairing
        """
        cr, uid, context = self.cr, self.uid, self.context
        nouvelobs_id, nouvelobs_bis_id = self.partner_nouvelobs_id, self.partner_nouvelobs_bis_id
        partner_model, allow_duplicate_wizard_model = self.partner_model, self.allow_duplicate_wizard_model

        # Check for reference data
        flds = ['is_duplicate_detected', 'is_duplicate_allowed', 'active', 'is_company']
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [not fields.get('active'), not fields.get('is_company')] + \
                    [fields.get('is_duplicate_detected', False), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Wrong expected reference data for this test (id=%s)' % pid)

        # Update nouvelobs_bis => duplicates: 2 detected, 0 allowed
        partner_model.write(cr, uid, [nouvelobs_bis_id], {'name': 'Nouvel Observateur'}, context=context)
        flds = ['is_duplicate_detected', 'is_duplicate_allowed']
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [not fields.get('is_duplicate_detected'), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate detection (id=%s)' % pid)

        # Allow duplicates => duplicates: 0 detected, 2 allowed
        ctx = {'active_model': 'res.partner',
               'active_ids': [nouvelobs_id, nouvelobs_bis_id]}
        ctx.update(context)
        wz_id = allow_duplicate_wizard_model.create(cr, uid, {}, context=ctx)
        allow_duplicate_wizard_model.button_allow_duplicate(cr, uid, wz_id, context=ctx)
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [fields.get('is_duplicate_detected', False), not fields.get('is_duplicate_allowed')]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate permission (id=%s)' % pid)

        # Undo allow duplicate on one partner => duplicates: 2 detected, 0 allowed
        partner_model.button_undo_allow_duplicate(cr, uid, [nouvelobs_id], context=context)
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [not fields.get('is_duplicate_detected'), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate detection (id=%s)' % pid)

        # Create one more 'nouvelobs' => duplicates: 3 detected, 0 allowed
        nouvelobs_ter_id = partner_model.create(cr, uid, {'name': 'Nouvel Observateur'}, context=context)
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id, nouvelobs_ter_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [not fields.get('is_duplicate_detected'), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate detection (id=%s)' % pid)

        # Invalidate partner => duplicates: 2 detected, 0 allowed
        partner_model.action_invalidate(cr, uid, [nouvelobs_ter_id], context=context)
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [not fields.get('is_duplicate_detected'), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate detection (id=%s)' % pid)
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_ter_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [fields.get('is_duplicate_detected', False), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate repairing (id=%s)' % pid)

        # Update nouvelobs_bis => duplicates: 0 detected, 0 allowed
        partner_model.write(cr, uid, [nouvelobs_id], {'name': 'Nouvel Observateur (Economat)'}, context=context)
        partner_fields = partner_model.read(cr, SUPERUSER_ID, [nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [fields.get('is_duplicate_detected', False), fields.get('is_duplicate_allowed', False)]
            self.assertFalse(any(bools), 'Update partner name fails with wrong duplicate repairing (id=%s)' % pid)

    def test_invalidate_partner(self):
        """
        =======================
        test_invalidate_partner
        =======================
        1) create a company and a user
        2) try to invalidate company's partner and user's partner and check that failed
        3) set active to false for the new user
        4) retry to invalidate the user's partner and check it succeed
        """
        company_test_id = self.company_model.create(self.cr, self.uid, {'name': '%s' % uuid4()})
        user_test_id = self.user_model.create(self.cr, SUPERUSER_ID, {'name': '%s' % uuid4(),
                                                                      'login': '%s' % uuid4()})

        company_test = self.company_model.browse(self.cr, self.uid, [company_test_id])[0]
        user_test = self.user_model.browse(self.cr, self.uid, [user_test_id])[0]

        self.assertRaises(orm.except_orm, self.partner_model.action_invalidate, self.cr, self.uid, [company_test.partner_id.id])
        self.assertRaises(orm.except_orm, self.partner_model.action_invalidate, self.cr, self.uid, [user_test.partner_id.id])

        self.user_model.write(self.cr, SUPERUSER_ID, [user_test.id], {'active': False})
        self.partner_model.action_invalidate(self.cr, self.uid, [user_test.partner_id.id])
        self.assertFalse(self.partner_model.read(self.cr, self.uid, [user_test.partner_id.id], ['active'])[0]['active'],
                         'Partner of The Duplicate Company Should Be Invalidate')

    def test_birth_date_duplicate_managment(self):
        """
        ===================================
        test_birth_date_duplicate_managment
        ===================================
        1) Create Partner named
            * A date 2010-10-10 (A1)
            * A date 2010-10-11 (A2)
            Check
                * A1 is not duplicate detected
                * A2 is not duplicate detected
        2) Update birth_date of A2 with 2010-10-10
            Check
                * A1 is duplicate detected
                * A2 is duplicate detected
        3) Update birth_date of A1 with 1990-10-10
            Check
                * A1 is not duplicate detected
                * A2 is not duplicate detected
        4) Create Partner names
            * A date False (A3)
            Check
                * All are duplicate detected
        5) Update birth_date of A3 with 1990-10-10
            Check
                A1 and A3 are duplicate detected
                A2 is not duplicate detected
        """
        cr, uid = self.cr, self.uid
        pids = []
        days = [10, 11]
        # Step 1
        for day in days:
            pids.append(self.partner_model.create(cr, uid,
                                         {'name': 'A',
                                          'birth_date': '2010-10-%s' % day}))
        document_values = self.partner_model.read(cr, uid, pids, ['is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 1 : 0 detected,0 allowed
        for document_value in document_values:
            bools = [document_value['is_duplicate_detected'],
                     document_value['is_duplicate_allowed']]
            self.assertFalse(any(bools), 'Partner %s Should Not Be Duplicate Concerned' % document_value['id'])
        # Step 2
        self.partner_model.write(cr, uid, [pids[1]], {'birth_date': '2010-10-%s' % days[0]})
        document_values = self.partner_model.read(cr, uid, pids, ['is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 2 : 1 detected,0 allowed
        for document_value in document_values:
            bools = [not document_value['is_duplicate_detected'],
                     document_value['is_duplicate_allowed']]
            self.assertFalse(any(bools), 'Partner %s Should Be Duplicate Detected Only' % document_value['id'])
        # Step 3
        last_birth_date = {'birth_date': '1990-10-10'}
        self.partner_model.write(cr, uid, [pids[0]], last_birth_date)
        document_values = self.partner_model.read(cr, uid, pids, ['is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 3 : 0 detected,0 allowed
        for document_value in document_values:
            bools = [document_value['is_duplicate_detected'],
                     document_value['is_duplicate_allowed']]
            self.assertFalse(any(bools), 'Partner %s Should Not Be Duplicate Concerned' % document_value['id'])
        # Step 4
        pids.append(self.partner_model.create(cr, uid, {'name': 'A',
                                                        'birth_date': last_birth_date['birth_date']}))
        document_values = self.partner_model.read(cr, uid, pids, ['birth_date', 'is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 4 : 2 detected, 1 not detected
        for document_value in document_values:
            if document_value['birth_date'] == last_birth_date['birth_date']:
                self.assertTrue(document_value['is_duplicate_detected'], 'Partner %s Should Be Duplicate Detected' % document_value['id'])
            else:
                self.assertFalse(document_value['is_duplicate_detected'], 'Partner %s Should Not Be Duplicate Detected' % document_value['id'])

    def test_identifier_unicity(self):
        """
        ===================================
        test_identifier_unicity
        ===================================
        """
        result = self.partner_model.search_read(self.cr, self.uid, [], ['identifier'], limit=1, order='identifier desc')
        if result:
            identifier = result[0]['identifier'] + 1000
        else:
            identifier = 3000

        self.partner_model.create(self.cr, self.uid,
                                         {'name': 'Test-identifier',
                                          'identifier': identifier})

        self.assertRaises(orm.except_orm, self.partner_model.create, self.cr, self.uid,
                                         {'name': 'Test-duplicate-identifier',
                                          'identifier': identifier})

    def test_change_identifier_sequence(self):
        """
        ===================================
        test_change_identifier_sequence
        ===================================
        """
        result = self.partner_model.search_read(self.cr, self.uid, [], ['identifier'], limit=1, order='identifier desc')
        if result:
            identifier = result[0]['identifier'] + 1000
        else:
            identifier = 3000

        self.partner_model.create(self.cr, self.uid,
                                         {'name': 'Test-identifier',
                                          'identifier': identifier})
        self.assertTrue(self.partner_model.update_identifier_next_number_sequence(self.cr, self.uid))
        sequence_id = self.registry('ir.model.data').get_object_reference(self.cr, self.uid, 'ficep_person', 'identifier_res_partner_seq')
        self.assertEqual(self.registry('ir.sequence').next_by_id(self.cr, self.uid, sequence_id[1]), str(identifier + 1))
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
