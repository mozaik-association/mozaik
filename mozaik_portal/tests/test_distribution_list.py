# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_portal, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_portal is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_portal is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_portal.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from uuid import uuid4
import openerp.tests.common as common

SUPERUSER_ID = common.ADMIN_USER_ID


class test_distribution_list(common.TransactionCase):

    def setUp(self):
        super(test_distribution_list, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

        self.p_obj = self.registry('res.partner')
        self.dl_obj = self.registry('distribution.list')

    def test_subscribe_to_newsletter(self):
        cr, uid, context = self.cr, self.uid, {}
        dst_model_id = self.registry('ir.model').search(
            self.cr, self.uid, [('model', '=', 'res.partner')])[0]
        vals = {
            'name': '%s' % uuid4(),
        }
        partner_id = self.dl_obj._get_partner(cr, uid, context=context)
        vals = {
            'name': '%s' % uuid4(),
            'newsletter': True,
            'dst_model_id': dst_model_id,
            'opt_out_ids': [(4, partner_id)],
        }
        dl_id = self.dl_obj.create(
            cr, uid, vals, context=context)
        self.dl_obj.subscribe_to_newsletter(cr, uid, [dl_id], context=context)
        dl_vals = self.dl_obj.read(
            cr, uid, dl_id, ['opt_in_ids', 'opt_out_ids'], context=context)
        self.assertFalse(dl_vals['opt_out_ids'],
                         'Should not be into opt_out_ids anymore')
        self.assertTrue(partner_id in dl_vals['opt_in_ids'],
                        'Should be into opt_in_ids')
        self.dl_obj.unsubscribe_to_newsletter(
            cr, uid, [dl_id], context=context)
        dl_vals = self.dl_obj.read(
            cr, uid, dl_id, ['opt_in_ids', 'opt_out_ids'], context=context)
        self.assertTrue(partner_id in dl_vals['opt_out_ids'],
                        'Should be into opt_out_ids')
