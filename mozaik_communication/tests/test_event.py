# -*- coding: utf-8 -*-
#
###############################################################################
#    Authors: Nemry Jonathan
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
###############################################################################
from openerp.tests import common


class test_event(common.TransactionCase):

    def setUp(self):
        super(test_event, self).setUp()

        self.event_obj = self.registry['event.event']
        self.event_reg_obj = self.registry['event.registration']
        self.partner_obj = self.registry['res.partner']
        self.email_coo_obj = self.registry['email.coordinate']
        self.phone_coo_obj = self.registry['phone.coordinate']
        self.phone_obj = self.registry['phone.phone']

    def test_cancel_registration(self):
        cr, uid, context = self.cr, self.uid, {'no_notify': True}
        vals = {
            'name': 'My Event',
            'date_begin': '2014-10-29 14:57:08',
            'date_end': '2014-10-29 15:57:08',
        }
        event_id = self.event_obj.create(cr, uid, vals, context=context)
        # create partner
        vals = {
            'name': 'Bill',
        }
        partner_id = self.partner_obj.create(cr, uid, vals, context=context)
        vals = {
            'event_id': event_id,
            'partner_id': partner_id,
        }
        reg_id = self.event_reg_obj.create(cr, uid, vals, context=context)
        self.event_reg_obj.button_reg_cancel(
            cr, uid, [reg_id], context=context)
        reg_ids = self.event_reg_obj.search(
            cr, uid, [('active', '=', False), ('id', '=', reg_id)],
            context=context)
        self.assertTrue(reg_ids, 'Should be deactivate')

    def test_get_coordinate(self):
        '''
        '''
        cr, uid, context = self.cr, self.uid, {'no_notify': True}
        # create event
        vals = {
            'name': 'My Event',
            'date_begin': '2014-10-29 14:57:08',
            'date_end': '2014-10-29 15:57:08',
        }
        self.event_obj.create(cr, uid, vals, context=context)
        # create partner
        vals = {
            'name': 'Bill',
        }
        partner_id = self.partner_obj.create(cr, uid, vals, context=context)

        # create email coordinate
        vals = {
            'partner_id': partner_id,
            'email': 'test@sample.com',
        }
        email_coo_id = self.email_coo_obj.create(
            cr, uid, vals, context=context)

        # create phone
        vals = {
            'name': '061412002',
            'type': 'fix',
        }
        phone_id = self.phone_obj.create(
            cr, uid, vals, context=context)

        # create phone_coordinate
        vals = {
            'partner_id': partner_id,
            'phone_id': phone_id,
        }
        self.phone_coo_obj.create(
            cr, uid, vals, context=context)

        vals = {
            'partner_id': partner_id,
        }
        self.event_reg_obj._get_coordinates(cr, uid, vals, context=context)
        partner = self.partner_obj.browse(cr, uid, partner_id, context=context)
        self.assertEqual(partner.display_name, vals['name'],
                         'Display name and registration name should be'
                         ' the same')
        phone = self.phone_obj.browse(cr, uid, phone_id, context=context)
        self.assertEqual(phone.name, vals['phone'],
                         'Phone name and registration phone should be'
                         ' the same')
        email_coo = self.email_coo_obj.browse(
            cr, uid, email_coo_id, context=context)
        self.assertEqual(email_coo.email, vals['email'],
                         'Email coordinate and registration email should be'
                         ' the same')
