# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import date, datetime
import logging
import random
import string
from uuid import uuid4

from anybox.testing.openerp import SharedSetupTransactionCase
from dateutil.relativedelta import relativedelta

from openerp.osv import orm
from openerp.tools import SUPERUSER_ID
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT


_logger = logging.getLogger(__name__)


class test_res_partner(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
    )

    _module_ns = 'mozaik_person'

    def setUp(self):
        super(test_res_partner, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.partner_model = self.registry('res.partner')
        self.company_model = self.registry('res.company')
        self.user_model = self.registry('res.users')
        self.allow_duplicate_wizard_model = self.registry(
            'allow.duplicate.wizard')

        self.partner_nouvelobs_id = self.ref(
            '%s.res_partner_nouvelobs' %
            self._module_ns)
        self.partner_nouvelobs_bis_id = self.ref(
            '%s.res_partner_nouvelobs_bis' %
            self._module_ns)
        self.partner_fgtb_id = self.ref(
            '%s.res_partner_fgtb' % self._module_ns)
        self.partner_marc_id = self.ref(
            '%s.res_partner_marc' % self._module_ns)

        self.context = {}

    def test_res_partner_names(self):
        """
        ======================
        test_res_partner_names
        ======================
        Test the overriding of the name_get method to compute display_name
        """
        cr, uid, context = self.cr, self.uid, self.context
        fgtb_id, marc_id = self.partner_fgtb_id, self.partner_marc_id
        partner_model = self.partner_model

        # Check for reference data
        vals = partner_model.read(
            cr,
            uid,
            [fgtb_id],
            ['is_company', 'identifier'],
            context=context)[0]
        self.assertTrue(
            vals['is_company'],
            'Wrong expected reference data for this test')
        vals = partner_model.read(
            cr,
            uid,
            [marc_id],
            ['is_company', 'identifier'],
            context=context)[0]
        self.assertFalse(
            vals['is_company'],
            'Wrong expected reference data for this test')

        # A/ Change various names of a company

        # 1/ name
        self.partner_model.write(
            cr, uid, [fgtb_id],
            {'name': 'newname', 'acronym': False}, context=context)
        rec = partner_model.browse(
            cr, uid, [fgtb_id], context=context)[0]
        self.assertEqual(
            rec.name, 'newname',
            'Update partner name fails with wrong name')
        self.assertEqual(
            rec.select_name,
            rec.name,
            'Update partner name fails with wrong select_name')
        self.assertEqual(
            rec.display_name, '%s-%s' % (rec.identifier, rec.select_name),
            'Update partner name fails with wrong display_name')

        # 2/ acronym
        self.partner_model.write(
            cr, uid, [fgtb_id], {
                'acronym': 'abbrev'}, context=context)
        rec = partner_model.browse(
            cr, uid, [fgtb_id], context=context)[0]
        self.assertEqual(
            rec.name, 'newname',
            'Update partner name fails with wrong name')
        self.assertEqual(
            rec.select_name, '%s (%s)' % (rec.name, 'abbrev'),
            'Update partner name fails with wrong select_name')
        self.assertEqual(
            rec.display_name, '%s-%s' % (rec.identifier, rec.select_name),
            'Update partner name fails with wrong display_name')

        # B/ Change various names of a contact

        # 1/ firstname, lastname
        self.partner_model.write(cr,
                                 uid,
                                 [marc_id],
                                 {'firstname': 'first',
                                  'lastname': 'last',
                                  'usual_firstname': False,
                                  'usual_lastname': False,
                                  },
                                 context=context)
        rec = partner_model.browse(
            cr, uid, [marc_id], context=context)[0]
        self.assertEqual(
            rec.name, '%s %s' % ('last', 'first'),
            'Update both partner first and last names fails with wrong name')
        self.assertEqual(
            rec.select_name, rec.name,
            'Update both partner first and last names fails with wrong '
            'select_name')
        self.assertEqual(
            rec.display_name, "%s-%s" % (rec.identifier, rec.select_name),
            'Update both partner first and last names fails with wrong '
            'display_name')

        # 2/ usual_firstname
        self.partner_model.write(
            cr, uid, [marc_id],
            {'usual_firstname': 'ufirst'}, context=context)
        rec = partner_model.browse(
            cr, uid, [marc_id], context=context)[0]
        self.assertEqual(
            rec.name, '%s %s' % ('last', 'first'),
            'Update partner usual_firstname fails with wrong name')
        self.assertEqual(
            rec.select_name,
            '%s %s (%s)' % ('last', 'ufirst', rec.name),
            'Update partner usual_firstname fails with wrong select_name')
        self.assertEqual(
            rec.display_name,
            '%s-%s' % (rec.identifier, rec.select_name),
            'Update partner usual_firstname fails with wrong select_name')

        # 3/ usual_lastname
        self.partner_model.write(
            cr, uid, [marc_id],
            {'usual_firstname': False, 'usual_lastname': 'ulast'},
            context=context)
        rec = partner_model.browse(
            cr, uid, [marc_id], context=context)[0]
        self.assertEqual(
            rec.name, '%s %s' % ('last', 'first'),
            'Update partner usual_lastname fails with wrong name')
        self.assertEqual(
            rec.select_name,
            '%s %s (%s)' % ('ulast', 'first', rec.name),
            'Update partner usual_lastname fails with wrong select_name')
        self.assertEqual(
            rec.display_name,
            '%s-%s' % (rec.identifier, rec.select_name),
            'Update partner usual_lastname fails with wrong display_name')

        # 4/ all
        vals = {
            'firstname': 'Ian', 'lastname': 'FLEMING',
            'usual_firstname': 'James', 'usual_lastname': 'BOND',
        }
        self.partner_model.write(
            cr, uid, [marc_id], vals, context=context)
        rec = partner_model.browse(
            cr, uid, [marc_id], context=context)[0]
        self.assertEqual(
            rec.name, '%s %s' % ('FLEMING', 'Ian'),
            'Update all partner names fails with wrong name')
        self.assertEqual(
            rec.select_name,
            '%s %s (%s)' % ('BOND', 'James', rec.name),
            'Update all partner names fails with wrong select_name')
        self.assertEqual(
            rec.display_name,
            '%s-%s' % (rec.identifier, rec.select_name),
            'Update all partner names fails with wrong display_name')
        self.assertEquals(
            rec.technical_name, 'bondjamesflemingian',
            'Technical name should be equals to display_name without uppercase'
            ' and without accents nor spaces nor special characters')
        self.assertEqual(
            rec.printable_name, '%s %s' % ('James', 'BOND'),
            'Update all partner names fails with wrong printable_name')

        # 5/ Test the capitalize mode
        vals = {
            'firstname': u'Carmelitá', 'lastname': u'de la Sígnora di Spaña',
            'usual_firstname': False, 'usual_lastname': False,
        }
        self.partner_model.write(
            cr, uid, [marc_id], vals, context=context)
        p = self.partner_model.browse(cr, uid, [marc_id])[0]
        name = self.partner_model.build_name(
            p, reverse_mode=True, capitalize_mode=True)
        self.assertEqual(
            name, u'Carmelitá de la SÍGNORA di SPAÑA',
            'Update all partner names fails with wrong capitalized name')

    def test_res_partner_duplicates(self):
        """
        ===========================
        test_res_partner_duplicates
        ===========================
        Test duplicate detection, permission and repairing
        """
        cr, uid, context = self.cr, self.uid, self.context
        nouvelobs_id = self.partner_nouvelobs_id
        nouvelobs_bis_id = self.partner_nouvelobs_bis_id
        partner_model = self.partner_model
        allow_duplicate_wizard_model = self.allow_duplicate_wizard_model

        # Check for reference data
        flds = [
            'is_duplicate_detected',
            'is_duplicate_allowed',
            'active',
            'is_company']
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                not fields.get('active'), not fields.get('is_company')] + [
                fields.get(
                    'is_duplicate_detected', False), fields.get(
                    'is_duplicate_allowed', False)]
            self.assertFalse(
                any(bools),
                'Wrong expected reference data for this test (id=%s)' %
                pid)

        # Update nouvelobs_bis => duplicates: 2 detected, 0 allowed
        partner_model.write(
            cr, uid, [nouvelobs_bis_id], {
                'name': 'Nouvel Observateur', 'is_company': True},
            context=context)
        flds = ['is_duplicate_detected', 'is_duplicate_allowed']
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                not fields.get('is_duplicate_detected'),
                fields.get(
                    'is_duplicate_allowed',
                    False)]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate detection '
                '(id=%s)' % pid)

        # Allow duplicates => duplicates: 0 detected, 2 allowed
        ctx = {'active_model': 'res.partner',
               'active_ids': [nouvelobs_id, nouvelobs_bis_id]}
        ctx.update(context)
        wz_id = allow_duplicate_wizard_model.create(cr, uid, {}, context=ctx)
        allow_duplicate_wizard_model.button_allow_duplicate(
            cr,
            uid,
            wz_id,
            context=ctx)
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                fields.get(
                    'is_duplicate_detected',
                    False),
                not fields.get('is_duplicate_allowed')]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate permission '
                '(id=%s)' % pid)

        # Undo allow duplicate on one partner => duplicates: 2 detected, 0
        # allowed
        partner_model.button_undo_allow_duplicate(
            cr,
            uid,
            [nouvelobs_id],
            context=context)
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                not fields.get('is_duplicate_detected'),
                fields.get(
                    'is_duplicate_allowed',
                    False)]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate detection '
                '(id=%s)' % pid)

        # Create one more 'nouvelobs' => duplicates: 3 detected, 0 allowed
        nouvelobs_ter_id = partner_model.create(
            cr, uid, {
                'name': 'Nouvel Observateur', 'is_company': True},
            context=context)
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id, nouvelobs_ter_id], flds,
            context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                not fields.get('is_duplicate_detected'),
                fields.get(
                    'is_duplicate_allowed',
                    False)]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate detection '
                '(id=%s)' % pid)

        # Invalidate partner => duplicates: 2 detected, 0 allowed
        partner_model.action_invalidate(
            cr,
            uid,
            [nouvelobs_ter_id],
            context=context)
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                not fields.get('is_duplicate_detected'),
                fields.get(
                    'is_duplicate_allowed',
                    False)]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate detection '
                '(id=%s)' % pid)
        partner_fields = partner_model.read(
            cr,
            SUPERUSER_ID,
            [nouvelobs_ter_id],
            flds,
            context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                fields.get(
                    'is_duplicate_detected', False), fields.get(
                    'is_duplicate_allowed', False)]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate repairing '
                '(id=%s)' % pid)

        # Update nouvelobs_bis => duplicates: 0 detected, 0 allowed
        partner_model.write(
            cr, uid, [nouvelobs_id], {
                'name': 'Nouvel Observateur (Economat)', 'is_company': True},
            context=context)
        partner_fields = partner_model.read(
            cr, SUPERUSER_ID, [
                nouvelobs_id, nouvelobs_bis_id], flds, context=context)
        for fields in partner_fields:
            pid = fields.get('id')
            bools = [
                fields.get(
                    'is_duplicate_detected', False), fields.get(
                    'is_duplicate_allowed', False)]
            self.assertFalse(
                any(bools),
                'Update partner name fails with wrong duplicate repairing '
                '(id=%s)' % pid)

    def test_invalidate_partner(self):
        """
        =======================
        test_invalidate_partner
        =======================
        1) create a company and a user
        2) try to invalidate user's partner and check that failed
        3) set active to false for the new user
        4) retry to invalidate the user's partner and check it succeed
        """
        user_test_id = self.user_model.create(
            self.cr, SUPERUSER_ID, {
                'name': '%s' %
                uuid4(), 'login': '%s' %
                uuid4()})

        user_test = self.user_model.browse(
            self.cr, self.uid, [user_test_id])[0]

        self.assertRaises(orm.except_orm,
                          self.partner_model.action_invalidate,
                          self.cr,
                          self.uid,
                          [user_test.partner_id.id])

        self.user_model.write(
            self.cr, SUPERUSER_ID, [
                user_test.id], {
                'active': False})
        self.partner_model.action_invalidate(
            self.cr, self.uid, [
                user_test.partner_id.id])
        self.assertFalse(
            self.partner_model.read(
                self.cr,
                self.uid,
                [user_test.partner_id.id],
                ['active'])[0]['active'],
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
            pids.append(
                self.partner_model.create(
                    cr, uid, {
                        'name': 'A', 'birth_date': '2010-10-%s' %
                        day}))
        document_values = self.partner_model.read(
            cr, uid, pids, [
                'is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 1 : 0 detected,0 allowed
        for document_value in document_values:
            bools = [document_value['is_duplicate_detected'],
                     document_value['is_duplicate_allowed']]
            self.assertFalse(
                any(bools),
                'Partner %s Should Not Be Duplicate Concerned' %
                document_value['id'])
        # Step 2
        self.partner_model.write(
            cr, uid, [
                pids[1]], {
                'birth_date': '2010-10-%s' %
                days[0]})
        document_values = self.partner_model.read(
            cr, uid, pids, [
                'is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 2 : 1 detected,0 allowed
        for document_value in document_values:
            bools = [not document_value['is_duplicate_detected'],
                     document_value['is_duplicate_allowed']]
            self.assertFalse(
                any(bools),
                'Partner %s Should Be Duplicate Detected Only' %
                document_value['id'])
        # Step 3
        last_birth_date = {'birth_date': '1990-10-10'}
        self.partner_model.write(cr, uid, [pids[0]], last_birth_date)
        document_values = self.partner_model.read(
            cr, uid, pids, [
                'is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 3 : 0 detected,0 allowed
        for document_value in document_values:
            bools = [document_value['is_duplicate_detected'],
                     document_value['is_duplicate_allowed']]
            self.assertFalse(
                any(bools),
                'Partner %s Should Not Be Duplicate Concerned' %
                document_value['id'])
        # Step 4
        pids.append(
            self.partner_model.create(
                cr, uid, {
                    'name': 'A', 'birth_date': last_birth_date['birth_date']}))
        document_values = self.partner_model.read(
            cr, uid, pids, [
                'birth_date', 'is_duplicate_detected', 'is_duplicate_allowed'])
        # Check 4 : 2 detected, 1 not detected
        for document_value in document_values:
            if document_value['birth_date'] == last_birth_date['birth_date']:
                self.assertTrue(
                    document_value['is_duplicate_detected'],
                    'Partner %s Should Be Duplicate Detected' %
                    document_value['id'])
            else:
                self.assertFalse(
                    document_value['is_duplicate_detected'],
                    'Partner %s Should Not Be Duplicate Detected' %
                    document_value['id'])

    def test_identifier_unicity(self):
        """
        ===================================
        test_identifier_unicity
        ===================================
        """
        result = self.partner_model.search_read(
            self.cr,
            self.uid,
            [],
            ['identifier'],
            limit=1,
            order='identifier desc')
        if result:
            identifier = result[0]['identifier'] + 1000
        else:
            identifier = 3000

        self.partner_model.create(self.cr, self.uid,
                                  {'name': 'Test-identifier',
                                   'identifier': identifier})

        self.assertRaises(
            orm.except_orm, self.partner_model.create, self.cr, self.uid, {
                'name': 'Test-duplicate-identifier', 'identifier': identifier})

    def test_change_identifier_sequence(self):
        """
        ===================================
        test_change_identifier_sequence
        ===================================
        """
        result = self.partner_model.search_read(
            self.cr,
            self.uid,
            [],
            ['identifier'],
            limit=1,
            order='identifier desc')
        if result:
            identifier = result[0]['identifier'] + 1000
        else:
            identifier = 3000

        self.partner_model.create(self.cr, self.uid,
                                  {'name': 'Test-identifier',
                                   'identifier': identifier})
        self.assertTrue(
            self.partner_model.update_identifier_next_number_sequence(
                self.cr,
                self.uid))
        sequence_id = self.registry('ir.model.data').get_object_reference(
            self.cr,
            self.uid,
            'mozaik_person',
            'identifier_res_partner_seq')
        self.assertEqual(
            self.registry('ir.sequence').next_by_id(
                self.cr, self.uid, sequence_id[1]), str(
                identifier + 1))

    def test_get_login(self):
        """
        ==============
        test_get_login
        ==============
        * Try to get login with an email an a birth date unknown
            ** Check that we receive 0 because no partner found
        * Create a partner with the previous email/birth_date
        * Re-Try to get login with same email and birth_date
            ** Check that login is login of a created user
            ** Check that the partner of this user has an identical partner_id
                that the created partner
            ** Check that user's group is only portal group
        * Re-try to get login with same email and birth_date
            ** Check that login is the same that before
        * Create a partner with same email and same birth_date
        * Re-try to get login with same email and same birth_date
            ** Check that login is '' because partner search is ambiguous
        * Add groups to the created user
            ** Check that login is '' because only portal user are admit
        Create a partner with an email and a birth date
        """
        cr, uid = self.cr, self.uid
        imd_obj = self.registry['ir.model.data']
        partner_obj = self.registry['res.partner']
        user_obj = self.registry['res.users']

        name = ''.join(
            random.choice(
                string.ascii_uppercase +
                string.digits) for _ in range(10))
        email = '%s@tst.te' % name
        birth_date = '1901-10-12'
        BAD_LOGIN = 'Bad received LOGIN'
        BAD_GROUP = 'Should be into Portal and only into Portal'

        # no partner with this email and this birth_date -> 0
        self.assertEqual(
            partner_obj.get_login(
                cr,
                uid,
                email,
                birth_date),
            '',
            BAD_LOGIN)

        partner_id = partner_obj.create(cr, uid, {'name': name,
                                                  'email': email,
                                                  'birth_date': birth_date})
        login = partner_obj.get_login(cr, uid, email, birth_date)

        # test that user is created
        self.assertFalse(login == '', BAD_LOGIN)

        # test that the partner is related to the user as well
        user_ids = user_obj.search(cr, uid, [('login', '=', login)])
        user = user_obj.browse(cr, uid, user_ids)[0]
        self.assertEquals(user.partner_id.id, partner_id, BAD_LOGIN)

        # test group
        _, group_id = imd_obj.get_object_reference(
            cr, uid, 'base', 'group_portal')
        self.assertTrue(len(user.groups_id) == 1 and
                        user.groups_id[0].id == group_id, BAD_GROUP)

        # re-try to find the same
        duplicated_uid = partner_obj.get_login(cr, uid, email, birth_date)
        self.assertEqual(login, duplicated_uid, BAD_LOGIN)
        partner_obj.create(cr, uid, {'name': '%s-2' % name,
                                     'email': email,
                                     'birth_date': birth_date})

        # 0 because of two partners are present into the database
        self.assertTrue(
            partner_obj.get_login(
                cr,
                uid,
                email,
                birth_date) == '',
            BAD_LOGIN)

        _, other_group_id = imd_obj.get_object_reference(
            cr, uid, 'base', 'group_user')
        user.write({'groups_id': [[4, other_group_id]]})

        # 0 because this is not only portal group
        self.assertTrue(
            partner_obj.get_login(
                cr,
                uid,
                email,
                birth_date) == '',
            BAD_GROUP)

    def test_age_computation(self):
        """
        Check value of age depending of the birth_date
        """
        cr, uid, context = self.cr, self.uid, {}
        age = 10
        birth_date = datetime.strftime(
            date.today() - relativedelta(years=age),
            DEFAULT_SERVER_DATE_FORMAT)
        vals = {
            'name': 'Mitch',
            'birth_date': birth_date,
        }
        partner_id = self.partner_model.create(cr, uid, vals, context=context)
        partner = self.partner_model.browse(
            cr, uid, partner_id, context=context)
        self.assertEquals(partner.age, age, 'Should be the same age')

    def test_lastname_firstname(self):
        vals = {
            'lastname': 'El Ghabri',
            'firstname': 'Mohssin',
            'name': 'El Ghabri Mohssin'
        }
        partner = self.env['res.partner'].create(vals)
        self.assertEqual(vals['lastname'], partner.lastname)
