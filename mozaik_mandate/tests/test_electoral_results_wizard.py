# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import tempfile
import base64
from openerp.tools.translate import _

from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.addons.mozaik_mandate.wizard \
     import electoral_results_wizard as wizard_class

_logger = logging.getLogger(__name__)


class test_electoral_results_wizard(SharedSetupTransactionCase):
    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'

    def setUp(self):
        super(test_electoral_results_wizard, self).setUp()
        self.district_01 = self.browse_ref('%s.electoral_district_01' %
                                           self._module_ns)
        self.legislature_01_id = self.ref('%s.legislature_01' %
                                           self._module_ns)
        self.sta_paul_communal = self.browse_ref('%s.sta_paul_communal' %
                                        self._module_ns)
        self.sta_pauline_communal = self.browse_ref('%s.sta_pauline_communal' %
                                           self._module_ns)
        self.sta_marc_communal = self.browse_ref('%s.sta_marc_communal' %
                                        self._module_ns)
        self.sta_thierry_communal = self.browse_ref('%s.sta_thierry_communal' %
                                           self._module_ns)
        self.sta_jacques_communal = self.browse_ref('%s.sta_jacques_communal' %
                                           self._module_ns)

        self.committee_id = self.ref('%s.sc_tete_huy_communale'
                                        % self._module_ns)

        committee_pool = self.registry('sta.selection.committee')
        candidature_pool = self.registry['sta.candidature']
        accepted_ids = [self.sta_paul_communal.id,
                        self.sta_pauline_communal.id,
                        self.sta_thierry_communal.id,
                        self.sta_jacques_communal.id]
        rejected_ids = [self.sta_marc_communal.id]

        candidature_pool.signal_workflow(self.cr,
                                         self.uid,
                                         accepted_ids,
                                         'button_suggest')

        candidature_pool.signal_workflow(self.cr,
                                         self.uid,
                                         rejected_ids,
                                         'button_reject')

        committee_pool.write(self.cr, self.uid, [self.committee_id],
                             {'decision_date': '2014-04-01'})
        committee_pool.button_accept_candidatures(self.cr,
                                                 self.uid,
                                                 [self.committee_id])

    def test_electoral_results_wizard_wrong_file(self):
        '''
            Import electoral results
        '''
        candidature_pool = self.registry['sta.candidature']
        candidature_pool.signal_workflow(self.cr,
                                         self.uid,
                                         [self.sta_paul_communal.id],
                                         'button_elected')
        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard_class.file_import_structure) + '\n')
        #wrong row size
        data = ['a', 'b']
        temp_file.write(','.join(data) + '\n')
        #votes non numerical
        data = ['test', '', 'Toto', 'a', '', '']
        temp_file.write(','.join(data) + '\n')
        #position non numerical
        data = ['test', '', 'Toto', '3', 'a', '']
        temp_file.write(','.join(data) + '\n')
        #position non elected non numerical
        data = ['test', '', 'Toto', '3', '2', 'a']
        temp_file.write(','.join(data) + '\n')
        #unknown district
        data = ['test', '', 'Toto', '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        #unknown candidate
        data = [self.district_01.name, '', 'Toto', '3', '2', '']
        temp_file.write(','.join(data) + '\n')
        #bad candidature state
        data = [self.district_01.name, '', self.sta_marc_communal.partner_name,
                '3', '2', '']
        temp_file.write(','.join(data) + '\n')
        #elected candidate with position non elected set
        data = [self.district_01.name, '', self.sta_paul_communal.partner_name,
                '3', '', '1']
        temp_file.write(','.join(data) + '\n')
        #inconsistent value for column E/S
        data = [self.district_01.name, 'B',
                self.sta_pauline_communal.partner_name, '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        #inconsistent value for column E/S with candidature settings
        data = [self.district_01.name, '',
                self.sta_thierry_communal.partner_name, '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        #Effective line with substitute candidature
        data = [self.district_01.name, 'E',
                self.sta_thierry_communal.partner_name, '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        #Substitute line with effective candidature
        data = [self.district_01.name, 'S',
                self.sta_pauline_communal.partner_name, '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        #Position non elected should not be set with e_S value
        data = [self.district_01.name, 'E',
                self.sta_pauline_communal.partner_name, '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        #Position and position non elected can not be set both
        data = [self.district_01.name, '',
                self.sta_paul_communal.partner_name, '3', '2', '1']
        temp_file.write(','.join(data) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [self.legislature_01_id],
            'active_model': 'legislature',
        }
        wizard_pool = self.registry('electoral.results.wizard')
        wiz_id = wizard_pool.create(
                            self.cr,
                            self.uid,
                            {'source_file': base64.encodestring(data_file)},
                            context=context)
        wizard_pool.validate_file(self.cr, self.uid, [wiz_id])

        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)

        self.assertEqual(len(wizard.error_lines), 14)
        for error in wizard.error_lines:

            if error.line_number == 2:
                expected_msg = _('Wrong number of columns(%s), '
                                 '%s expected!') % \
                                (2, len(wizard_class.file_import_structure))
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 3:
                expected_msg = _('Votes value should be integer: %s') % 'a'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 4:
                expected_msg = _('Position value should be integer: %s') % 'a'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 5:
                expected_msg = _('Position non elected value should '
                                 'be integer: %s') % 'a'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 6:
                expected_msg = _('Unknown district: %s') % 'test'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 7:
                expected_msg = _('Unknown candidate: %s') % 'Toto'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 8:
                expected_msg = _('Inconsistent state for candidature: %s') % \
                                'rejected'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 9:
                expected_msg = _('Candidate is elected but position '
                                  'non elected (%s) is set') % '1'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 10:
                expected_msg = _('Inconsistent value for column E/S: %s') % \
                                 'B'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 11:
                expected_msg = _('Candidature: inconsistent value for '
                                 'column E/S: should be %s') % 'S'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 12:
                expected_msg = _('Candidature is not flagged as effective')
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 13:
                expected_msg = _('Candidature is not flagged as substitute')
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 14:
                expected_msg = _('Position non elected is incompatible '
                                 'with e_s value: %s') % 'E'
                self.assertEquals(error.error_msg, expected_msg)

            elif error.line_number == 15:
                expected_msg = _('Position(%s) and position non elected(%s) '
                                 'can not be set both') % ('2', '1')
                self.assertEquals(error.error_msg, expected_msg)
            else:
                pass

    def test_electoral_results_wizard_elected(self):
        '''
            Import electoral results
        '''
        candidature_pool = self.registry['sta.candidature']

        used_ids = [self.sta_paul_communal.id,
                    self.sta_pauline_communal.id,
                    self.sta_jacques_communal.id
                    ]
        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard_class.file_import_structure) + '\n')

        data = [self.district_01.name, '',
                self.sta_paul_communal.partner_name, '1258', '1', '']
        temp_file.write(','.join(data) + '\n')

        data = [self.district_01.name, 'E',
                self.sta_pauline_communal.partner_name, '1258', '1', '']
        temp_file.write(','.join(data) + '\n')

        data = [self.district_01.name, 'S',
                self.sta_jacques_communal.partner_name, '1258', '1', '']
        temp_file.write(','.join(data) + '\n')
        data = [self.district_01.name, 'E',
                self.sta_jacques_communal.partner_name, '1258', '1', '']
        temp_file.write(','.join(data) + '\n')

        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [self.legislature_01_id],
            'active_model': 'legislature',
        }
        wizard_pool = self.registry('electoral.results.wizard')
        wiz_id = wizard_pool.create(
                            self.cr,
                            self.uid,
                            {'source_file': base64.encodestring(data_file)},
                            context=context)
        wizard_pool.validate_file(self.cr, self.uid, [wiz_id])

        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)

        self.assertEqual(len(wizard.error_lines), 0)

        wizard_pool.import_file(self.cr, self.uid, [wiz_id])

        for candidature in candidature_pool.browse(self.cr,
                                                   self.uid,
                                                   used_ids):
            self.assertEqual(candidature.state, 'elected')
            self.assertEqual(candidature.election_effective_position, 1)
            self.assertEqual(candidature.effective_votes, 1258)

    def test_electoral_results_wizard_non_elected(self):
        '''
            Import electoral results
        '''
        candidature_pool = self.registry['sta.candidature']

        used_ids = [self.sta_paul_communal.id,
                    self.sta_pauline_communal.id,
                    self.sta_jacques_communal.id
                    ]
        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard_class.file_import_structure) + '\n')

        data = [self.district_01.name, '',
                self.sta_paul_communal.partner_name, '1258', '', '1']
        temp_file.write(','.join(data) + '\n')

        data = [self.district_01.name, 'E',
                self.sta_pauline_communal.partner_name, '1258', '0', '']
        temp_file.write(','.join(data) + '\n')

        data = [self.district_01.name, 'S',
                self.sta_jacques_communal.partner_name, '1258', '1', '']
        temp_file.write(','.join(data) + '\n')
        data = [self.district_01.name, 'E',
                self.sta_jacques_communal.partner_name, '1258', '0', '']
        temp_file.write(','.join(data) + '\n')

        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [self.legislature_01_id],
            'active_model': 'legislature',
        }
        wizard_pool = self.registry('electoral.results.wizard')
        wiz_id = wizard_pool.create(
                            self.cr,
                            self.uid,
                            {'source_file': base64.encodestring(data_file)},
                            context=context)
        wizard_pool.validate_file(self.cr, self.uid, [wiz_id])

        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id)

        self.assertEqual(len(wizard.error_lines), 0)

        wizard_pool.import_file(self.cr, self.uid, [wiz_id])

        for candidature in candidature_pool.browse(self.cr,
                                                   self.uid,
                                                   used_ids):
            self.assertEqual(candidature.state, 'non-elected')
            if candidature.id == self.sta_paul_communal.id:
                self.assertEqual(candidature.election_substitute_position, 1)
                self.assertEqual(candidature.substitute_votes, 1258)
            else:
                self.assertEqual(candidature.election_effective_position, 0)
                self.assertEqual(candidature.effective_votes, 1258)
