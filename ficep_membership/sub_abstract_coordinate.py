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
from openerp.osv import orm
from openerp.tools import SUPERUSER_ID


class sub_abstract_coordinate(orm.AbstractModel):

    def _update_notify_followers(
            self, cr, uid, ids, partner_ids, context=None):
        self.pool['res.partner']._update_follower(
            cr, uid, partner_ids, context=context)
        subtype = 'ficep_membership.main_%s_notification' %\
            self._discriminant_field
        for i in ids:
            self._message_post(
                cr, uid, i, subtype=subtype, context=context)

    _track = {}
    _update_track = {}

    _name = 'sub.abstract.coordinate'

    def write(self, cr, uid, ids, vals, context=None):
        '''
        update and notify follower if is_main is True
        '''
        not_main_ids = self.search(
            cr, uid, [('is_main', '=', False),
                      ('id', 'in', ids)],
            context=context)
        res = super(sub_abstract_coordinate, self).write(
            cr, uid, ids, vals, context=context)
        if vals.get('is_main', False):
            partner_ids = []
            # assure change is well made after write
            new_main_ids = self.search(
                cr, uid, [('is_main', '=', True), ('id', 'in', not_main_ids)],
                context=context)
            if not vals.get('partner_id', False):
                for pc in self.browse(cr, uid, new_main_ids, context=context):
                    partner_ids.append(pc.partner_id.id)
            else:
                partner_ids.append(vals['partner_id'])

            self._update_notify_followers(
                cr, SUPERUSER_ID, new_main_ids, partner_ids, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        '''
        update and notify follower if is_main is True
        '''
        context = context or {}
        res = super(sub_abstract_coordinate, self).create(
            cr, uid, vals, context=context)
        if vals.get('is_main', False) and not context.get('no_notify', False):
            partner_id = vals['partner_id']
            self._update_notify_followers(
                cr, SUPERUSER_ID, [res], [partner_id], context=context)
        return res

    def _register_hook(self, cr):
        '''
        update track dict with new values
        '''
        super(sub_abstract_coordinate, self)._register_hook(cr)
        self._track.update(self._update_track)
