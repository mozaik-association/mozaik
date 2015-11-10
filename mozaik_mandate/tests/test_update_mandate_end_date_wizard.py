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
from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class test_update_mandate_end_date_wizard(object):
    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'mozaik_mandate'
    mandate = False
    model = False
    wizard = False

    def setUp(self):
        super(test_update_mandate_end_date_wizard, self).setUp()

    def test_update_mandate_end_date(self):
        '''
            Test 2 features of wizard:
                - set end date and inactivate an opened mandate
                - update end date of an inactive mandate
        '''
        context = {
            'active_ids': [self.mandate.id],
            'active_model': self.model,
            'mode': 'end_date',
        }
        tomorrow = datetime.now() + timedelta(days=1)
        last_week = datetime.now() - timedelta(days=7)
        last_month = datetime.now() - timedelta(days=30)

        wizard_pool = self.registry(self.wizard)
        wiz_id = wizard_pool.create(self.cr,
                                    self.uid,
                                    {'mandate_end_date': tomorrow},
                                    context=context)
        self.assertRaises(orm.except_orm,
                          wizard_pool.set_mandate_end_date,
                          self.cr,
                          self.uid,
                          wiz_id,
                          {})
        # Finish and inactive an opened mandate
        wizard_pool.write(self.cr,
                          self.uid,
                          wiz_id,
                          {'mandate_end_date': last_week})
        wizard_pool.set_mandate_end_date(self.cr,
                                         self.uid,
                                         wiz_id,
                                         context=context)
        self.mandate = self.registry[self.model].browse(self.cr,
                                                        self.uid,
                                                        self.mandate.id)
        self.assertFalse(self.mandate.active)
        self.assertEqual(self.mandate.end_date, last_week.strftime('%Y-%m-%d'))

        # Update end date of a finished mandate
        wizard_pool.write(self.cr,
                          self.uid,
                          wiz_id,
                          {'mandate_end_date': last_month})

        wizard_pool.set_mandate_end_date(self.cr,
                                         self.uid,
                                         wiz_id,
                                         context=context)

        self.assertFalse(self.mandate.active)
        self.assertEqual(self.mandate.end_date,
                         last_month.strftime('%Y-%m-%d'))

    def test_reactivate_mandate(self):
        '''
            Test the reactivation of an inactive mandate
        '''
        context = {
            'active_ids': [self.mandate.id],
            'active_model': self.model,
            'mode': 'reactivate',
        }
        last_week = datetime.now() - timedelta(days=7)
        last_month = datetime.now() - timedelta(days=30)
        next_month = datetime.now() + timedelta(days=30)

        wizard_pool = self.registry(self.wizard)

        # Inactivate mandate
        wiz_id = wizard_pool.create(self.cr,
                                    self.uid,
                                    {'mandate_end_date': last_week},
                                    context=context)
        wizard_pool.set_mandate_end_date(self.cr,
                                         self.uid,
                                         wiz_id,
                                         context=context)
        self.assertFalse(self.mandate.active)

        # Reactivate mandate
        wiz_id = wizard_pool.create(self.cr,
                                    self.uid,
                                    {'mandate_deadline_date': last_month},
                                    context=context)
        self.assertRaises(orm.except_orm,
                          wizard_pool.reactivate_mandate,
                          self.cr,
                          self.uid,
                          wiz_id,
                          {})

        wizard_pool.write(self.cr,
                          self.uid,
                          wiz_id,
                          {'mandate_deadline_date': next_month})

        wizard_pool.reactivate_mandate(self.cr,
                                       self.uid,
                                       wiz_id,
                                       context=context)

        self.assertTrue(self.mandate.active)
        self.assertEqual(self.mandate.deadline_date,
                         next_month.strftime('%Y-%m-%d'))

    def test_reactivate_active_mandate(self):
        '''
            Test the reactivation of an active mandate
        '''
        context = {
            'active_ids': [self.mandate.id],
            'active_model': self.model,
            'mode': 'reactivate',
        }
        next_month = datetime.now() + timedelta(days=30)

        wizard_pool = self.registry(self.wizard)

        self.assertTrue(self.mandate.active)

        # Reactivate mandate
        wiz_id = wizard_pool.create(self.cr,
                                    self.uid,
                                    {'mandate_deadline_date': next_month},
                                    context=context)
        wizard = wizard_pool.browse(self.cr, self.uid, wiz_id, context=context)
        self.assertEqual(wizard.message,
                         "The selected mandate is already active!")


class update_sta_mandate_end_date_wizard(test_update_mandate_end_date_wizard,
                                         SharedSetupTransactionCase):

    def setUp(self):
        self.mandate = self.browse_ref('%s.stam_thierry_bourgmestre'
                                       % self._module_ns)
        self.model = 'sta.mandate'
        self.wizard = 'update.sta.mandate.end.date.wizard'
        super(update_sta_mandate_end_date_wizard, self).setUp()

    def test_reactivate_mandate(self):
        return

    def test_reactivate_active_mandate(self):
        return


class update_int_mandate_end_date_wizard(test_update_mandate_end_date_wizard,
                                         SharedSetupTransactionCase):

    def setUp(self):
        self.mandate = self.browse_ref('%s.intm_paul_regional'
                                       % self._module_ns)
        self.model = 'int.mandate'
        self.wizard = 'update.int.mandate.end.date.wizard'
        super(update_int_mandate_end_date_wizard, self).setUp()


class update_ext_mandate_end_date_wizard(test_update_mandate_end_date_wizard,
                                         SharedSetupTransactionCase):

    def setUp(self):
        self.mandate = self.browse_ref('%s.extm_paul_membre_ag'
                                       % self._module_ns)
        self.model = 'ext.mandate'
        self.wizard = 'update.ext.mandate.end.date.wizard'
        super(update_ext_mandate_end_date_wizard, self).setUp()
