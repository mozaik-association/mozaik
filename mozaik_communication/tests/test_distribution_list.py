# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from uuid import uuid4

import openerp.tests.common as common

_logger = logging.getLogger(__name__)

DB = common.DB
SUPERUSER_ID = common.ADMIN_USER_ID


class test_distribution_list(common.TransactionCase):

    _module_ns = 'distribution_list'

    def setUp(self):
        super(test_distribution_list, self).setUp()
        self.user_obj = self.registry('res.users')
        self.partner_obj = self.registry('res.partner')
        self.dl_obj = self.registry('distribution.list')
        self.mail_obj = self.registry('mail.mail')
        self.int_instance_obj = self.registry('int.instance')
        self.email_coordinate_obj = self.registry('email.coordinate')

        self.partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_only_owner_forward(self):
        cr, uid, context = self.cr, self.uid, {}
        # create the partner
        name = '%s' % uuid4()
        vals = {
            'name': name,
        }
        partner_id = self.partner_obj.create(
            cr, uid, vals, context=context)
        default_instance_id = self.int_instance_obj.get_default(
            cr, uid, context=context)
        # create the user
        vals = {
            'name': name,
            'login': name,
            'signature': name,
            'partner_id': partner_id,
            'company_id': self.ref('base.main_company'),
            'groups_id': [(6, 0, [
                self.ref('mozaik_base.mozaik_res_groups_officer')])],
            'int_instance_m2m_ids': [(6, 0, [default_instance_id])]
        }
        user_id = self.user_obj.create(
            cr, uid, vals, context=context)

        # set email after to avoid MailDeliveryException
        vals = {
            'partner_id': partner_id,
            'email': '%s@test.eu' % name,
        }
        e_id = self.email_coordinate_obj.create(
            cr, uid, vals, context=context)

        dl_name = '%s' % uuid4()
        vals = {
            'name': dl_name,
            'int_instance_id': default_instance_id,
            'dst_model_id': self.partner_model_id,
            'mail_forwarding': True,
        }
        dl_id = self.dl_obj.create(cr, uid, vals, context=context)
        msg = {
            'email_from': "<%s@test.eu>" % name,
            'subject': 'test',
            'body': 'body',
        }
        self.dl_obj.distribution_list_forwarding(
            cr, uid, msg, dl_id, context=context)
        mail_ids = self.mail_obj.search(
            cr, uid,
            [('res_id', '=', partner_id), ('model', '=', 'res.partner')],
            context=context)
        self.assertFalse(mail_ids, 'Partner of the mailing object is not into '
                         'the owner of the distribution list so it should not '
                         'be possible to make a mail forwarding')
        # add user to the owner
        vals = {
            'res_users_ids': [(6, 0, [user_id])]
        }
        self.dl_obj.write(cr, uid, [dl_id], vals, context=context)
        self.dl_obj.distribution_list_forwarding(
            cr, uid, msg, dl_id, context=context)
        mail_ids = self.mail_obj.search(
            cr, uid,
            [('res_id', '=', e_id), ('model', '=', 'email.coordinate')],
            context=context)
        self.assertTrue(mail_ids, 'Partner of the mailing object is into '
                        'the owner of the distribution list so it should '
                        'be possible to make a mail forwarding')
