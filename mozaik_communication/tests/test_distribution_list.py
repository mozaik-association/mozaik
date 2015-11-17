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
import psycopg2
from anybox.testing.openerp import SharedSetupTransactionCase

import openerp.tests.common as common
from openerp.addons.mozaik_base import testtool

_logger = logging.getLogger(__name__)

SUPERUSER_ID = common.ADMIN_USER_ID


class test_distribution_list(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_email/tests/data/email_data.xml',
        '../../mozaik_address/tests/data/reference_data.xml',
        '../../mozaik_address/tests/data/address_data.xml',
        'data/communication_data.xml',
    )

    _module_ns = 'mozaik_communication'

    def setUp(self):
        super(test_distribution_list, self).setUp()
        self.user_obj = self.registry('res.users')
        self.partner_obj = self.registry('res.partner')
        self.dl_obj = self.registry('distribution.list')
        self.mail_obj = self.registry('mail.mail')
        self.int_instance_obj = self.registry('int.instance')
        self.ec_obj = self.registry('email.coordinate')
        self.pc_obj = self.registry('postal.coordinate')
        self.virtrg_obj = self.registry('virtual.target')
        self.evr_lst_id = self.ref('%s.everybody_list' % self._module_ns)

        self.partner_model_id = self.registry('ir.model').search(
            self.cr, SUPERUSER_ID, [('model', '=', 'res.partner')])[0]

        self.usr = self.create_an_officier()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def create_an_officier(self):
        cr, uid, context = self.cr, self.uid, {}
        name = '%s' % uuid4()

        # create the partner
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
            'partner_id': partner_id,
            'company_id': self.ref('base.main_company'),
            'groups_id': [(6, 0, [
                self.ref('mozaik_base.mozaik_res_groups_officer')])],
            'int_instance_m2m_ids': [(6, 0, [default_instance_id])]
        }
        user_id = self.user_obj.create(
            cr, uid, vals, context=context)
        return self.user_obj.browse(cr, uid, user_id, context=context)

    def test_only_owner_forward(self):
        cr, uid, context = self.cr, self.uid, {}
        name = '%s' % uuid4()

        # set email after to avoid MailDeliveryException
        vals = {
            'partner_id': self.usr.partner_id.id,
            'email': '%s@test.eu' % name,
        }
        e_id = self.ec_obj.create(cr, uid, vals, context=context)

        dl_id = self.evr_lst_id
        msg = {
            'email_from': "<%s@test.eu>" % name,
            'subject': 'test',
            'body': 'body',
        }
        self.dl_obj.distribution_list_forwarding(
            cr, uid, msg, dl_id, context=context)
        mail_ids = self.mail_obj.search(
            cr, uid,
            [('res_id', '=', self.usr.partner_id.id),
             ('model', '=', 'res.partner')],
            context=context)
        self.assertFalse(mail_ids, 'Partner of the mailing object is not into '
                         'the owner of the distribution list so it should not '
                         'be possible to make a mail forwarding')
        # add user to the owner
        vals = {
            'res_users_ids': [(6, 0, [self.usr.id])]
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
        vals = {
            'res_users_ids': [(3, self.usr.id, False)],
            'res_partner_m2m_ids': [(6, 0, [self.usr.partner_id.id])],
        }
        self.dl_obj.write(cr, uid, [dl_id], vals, context=context)
        self.dl_obj.distribution_list_forwarding(
            cr, uid, msg, dl_id, context=context)
        mail_ids = self.mail_obj.search(
            cr, uid,
            [('res_id', '=', e_id), ('model', '=', 'email.coordinate')],
            context=context)
        self.assertTrue(mail_ids, 'Partner of the mailing object is into '
                        'the allowed partner of the distribution list so'
                        'it should be possible to make a mail forwarding')

    def test_newsletter_code_unique(self):
        cr, uid, context = self.cr, self.uid, {}
        vals = dict(name='Newsletter Sample 1',
                    code='SAMPLE1',
                    newsletter=True)
        self.dl_obj.create(cr, uid, vals, context=context)
        vals = dict(name='Newsletter Sample 2',
                    code='SAMPLE1',
                    newsletter=True)
        with testtool.disable_log_error(cr):
            self.assertRaises(psycopg2.IntegrityError,
                              self.dl_obj.create,
                              cr, uid, vals, context)

    def test_notify_owner_on_alias_change(self):
        cr, uid, context = self.cr, self.uid, {}
        dl_name = '%s' % uuid4()
        default_instance_id = self.usr.int_instance_m2m_ids.ids[0]

        vals = {
            'name': dl_name,
            'int_instance_id': default_instance_id,
            'dst_model_id': self.partner_model_id,
            'mail_forwarding': True,
            'alias_name': 'xxx',
            'res_users_ids': [(6, False, [uid, self.usr.id])]
        }
        dl_id = self.dl_obj.create(cr, uid, vals, context=context)

        vals = {
            'alias_name': "yyy"
        }
        self.dl_obj.write(cr, uid, dl_id, vals, context=context)

        # owner should notified
        mail_ids = self.registry('mail.mail').search(cr, uid, [
            ('subject', 'ilike', dl_name),
            ('recipient_ids', 'in', self.usr.partner_id.id)], context=context)
        self.assertEqual(len(mail_ids), 1)

    def test_complex_distribution_list_ids(self):
        cr, uid, context = self.cr, self.uid, {}

        # create a vip email
        p_id = self.ref('%s.res_partner_thierry' % self._module_ns)
        ec_id = self.ec_obj.create(
            cr, uid,
            {'partner_id': p_id, 'email': 'x23@example.com', 'vip': True})

        dl_id = self.evr_lst_id
        oid = self.usr.id

        # virtual_target, admin
        a_main_ids, a_alternative_ids = \
            self.dl_obj.get_complex_distribution_list_ids(
                cr, uid, [dl_id], context=context)
        a_search_ids = self.virtrg_obj.search(
            cr, uid, [], context=context)
        self.assertFalse(a_alternative_ids)
        self.assertEqual(set(a_main_ids), set(a_search_ids))

        # virtual_target, other user
        u_main_ids = \
            self.dl_obj.get_complex_distribution_list_ids(
                cr, oid, [dl_id], context=context)[0]
        u_search_ids = self.virtrg_obj.search(
            cr, oid, [], context=context)
        self.assertEqual(set(u_main_ids), set(u_search_ids))
        self.assertEqual(set(a_main_ids), set(u_main_ids))

        context = dict(
            main_object_field='email_coordinate_id',
            main_object_domain=[],
            main_target_model='email.coordinate',
            alternative_object_field='postal_coordinate_id',
            alternative_object_domain=[('email_coordinate_id', '=', False)],
            alternative_target_model='postal.coordinate',
        )

        # email_coordinate_id, postal_coordinate_id, admin
        ac_main_ids, ac_alternative_ids = \
            self.dl_obj.get_complex_distribution_list_ids(
                cr, uid, [dl_id], context=context)
        self.assertTrue(ec_id in ac_main_ids)
        vals = self.virtrg_obj.search_read(
            cr, uid, domain=[('email_coordinate_id', '!=', False)],
            fields=['email_coordinate_id'], context=context)
        ac_search_ids = [d['email_coordinate_id'][0] for d in vals]
        self.assertEqual(set(ac_main_ids), set(ac_search_ids))
        vals = self.virtrg_obj.search_read(
            cr, uid, domain=[('email_coordinate_id', '=', False),
                             ('postal_coordinate_id', '!=', False)],
            fields=['postal_coordinate_id'], context=context)
        acp_search_ids = [d['postal_coordinate_id'][0] for d in vals]
        self.assertEqual(set(ac_alternative_ids), set(acp_search_ids))
        inactive_ids = self.virtrg_obj.search(
            cr, uid, [('active', '=', False)], context=context)

        e_vip_ids = [
            e.id for e
            in self.ec_obj.browse(cr, uid, ac_main_ids, context=context)
            if e.vip
        ]

        p_vip_ids = [
            p.id for p
            in self.pc_obj.browse(cr, uid, ac_alternative_ids, context=context)
            if p.vip
        ]

        # email_coordinate_id, postal_coordinate_id, other user
        uc_main_ids, uc_alternative_ids = \
            self.dl_obj.get_complex_distribution_list_ids(
                cr, oid, [dl_id], context=context)
        self.assertFalse(ec_id in uc_main_ids)
        vals = self.virtrg_obj.search_read(
            cr, oid, domain=[('email_coordinate_id', '!=', False)],
            fields=['email_coordinate_id'], context=context)
        uc_search_ids = [d['email_coordinate_id'][0] for d in vals]
        self.assertEqual(set(uc_main_ids), set(uc_search_ids) - set(e_vip_ids))
        vals = self.virtrg_obj.search_read(
            cr, oid, domain=[('email_coordinate_id', '=', False),
                             ('postal_coordinate_id', '!=', False)],
            fields=['postal_coordinate_id'], context=context)
        ucp_search_ids = [d['postal_coordinate_id'][0] for d in vals]
        self.assertEqual(
            set(uc_alternative_ids), set(ucp_search_ids) - set(p_vip_ids))

        context = dict(
            main_object_field='id',
            main_object_domain=[],
            main_target_model='virtual.target',
            active_test=False,
        )

        # virtual target, admin, inactive
        aa_main_ids = \
            self.dl_obj.get_complex_distribution_list_ids(
                cr, uid, [dl_id], context=context)[0]
        self.assertEqual(
            set(aa_main_ids) - set(inactive_ids), set(a_main_ids))

        pass
