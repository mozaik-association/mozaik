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
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.osv import orm

_logger = logging.getLogger(__name__)


class test_NAME(SharedSetupTransactionCase):

    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        'data/XXX_data.xml',
    )

    _module_ns = 'ficep_XXX'

    def setUp(self):
        super(test_NAME, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.partner_model = self.registry('res.partner')

        self.model_of_xxx_id = self.ref('%s.model_of_xxx_id' % self._module_ns)
        self.model_of_yyy_id = self.ref('%s.model_of_yyy_id' % self._module_ns)

        self.context = self.partner_model.context_get(self.cr, self.uid)

    def test_NAME_xxx(self):
        """
        =============
        test_NAME_xxx
        =============
        Test ...
        """
        cr, uid, context = self.cr, self.uid, self.context
        xxx_id = self.model_of_xxx_id
        partner_model = self.partner_model

        # Check for reference data
        vals = partner_model.read(
            cr, uid, [xxx_id], ['fld1', 'fld2'], context=context)[0]
        self.assertTrue(
            vals['fld1'], 'Wrong expected reference data for this test')
        self.assertEqual(
            vals['fld2'], 'hello',
            'Wrong expected reference data for this test')

        # ...

        self.assertTrue(True, 'Update... fails with wrong...')
        self.assertFalse(True, 'Update... fails with wrong...')
        self.assertEqual(vals['a'], '?!?', 'Update... fails with wrong...')

        # ...

        self.assertRaises(
            orm.except_orm,
            partner_model.write,
            cr, uid, xxx_id, {'is_company': True})
