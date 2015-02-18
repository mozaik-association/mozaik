# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of asynchronous_batch_mailings, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     asynchronous_batch_mailings is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     asynchronous_batch_mailings is distributed in the hope
#     that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with asynchronous_batch_mailings.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.asynchronous_batch_mailings.wizard import \
    mail_compose_message as fc

ADMIN_USER_ID = common.ADMIN_USER_ID


class test_async_mail_send(common.TransactionCase):

    def setUp(self):
        super(test_async_mail_send, self).setUp()

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_async_send_mail(self):
        """
        This test will check that the method create a right mail.mail
        from the passing values of the wizard.
        """
        cr, uid = self.cr, self.uid
        context = {
            'lang': 'en_US',
            'tz': False,
            'uid': 1,
            'show_reload': True,
            'default_composition_mode': 'mass_mail',
            'default_model': 'res.partner'
        }
        ir_att_obj = self.registry['ir.attachment']
        vals = {
            'datas': 'bWlncmF0aW9uIHRlc3Q=',
            'datas_fname': 'RedHat_spec.doc',
            'name': 'RedHat_spec.doc',
        }
        attachment_id = ir_att_obj.create(cr, uid, vals, context=context)
        vals = {
            'name': 'Mitch',
            'email': 'mitch@mi.tch',
        }

        mail_vals = {
            'composition_mode': 'mass_mail',
            'body': '<p>sample body</p>',
            'use_active_domain': False,
            'attachment_ids': [[6, False, [attachment_id]]],
            'template_id': 1,
            'parent_id': False,
            'notify': False,
            'no_auto_thread': False,
            'reply_to': False,
            'record_name': 'a',
            'model': 'res.partner',
            'partner_ids': [[6, False, []]],
            'res_id': 6,
            'email_from': 'Administrator <admin@example.com>',
            'subject': 'v15rIke7MpaRhg15FvqRjzet'
        }
        model_name = "mail.compose.message"
        session = ConnectorSession(self.cr, ADMIN_USER_ID, context=context)
        fc.do_send_mail(session, model_name, mail_vals)
        model_name = "mail.mail"
        model_mail = self.registry(model_name)
        mail_ids = model_mail.search(
            self.cr, ADMIN_USER_ID,
            [('subject', '=', 'v15rIke7MpaRhg15FvqRjzet')], context={})
        self.assertEqual(len(mail_ids) < 1, False,
                         "Mail Should Have Been Created")

        # Test the content of the mail
        read_mail = model_mail.browse(self.cr, ADMIN_USER_ID, mail_ids[0])
        self.assertEqual(read_mail.body, '<p>sample body</p>')
        self.assertEqual(read_mail.attachment_ids[0].name, "RedHat_spec.doc")
