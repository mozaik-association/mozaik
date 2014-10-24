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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields


class distribution_list(orm.Model):

    def _get_main_object(self, cr, uid, ids, context=None):
        return 'partner_id'

    def _get_partner(self, cr, uid, context=None):
        user_obj = self.pool['res.users']
        return user_obj.read(
            cr, SUPERUSER_ID, uid, ['partner_id'],
            context=context)['partner_id'][0]

    def _update_opt(self, cr, uid, ids, mode, context=None):
        partner_id = self._get_partner(cr, uid, context=context)
        for dl_id in ids:
            self.update_opt(
                cr, SUPERUSER_ID, dl_id, [partner_id], mode=mode,
                context=context)

    def _compute_subscribe(self, cr, uid, ids, name, args, context=None):
        '''
        Check if the partner of the current user is into
        the distribution list or not
        :rtype: {id: boolean}
        '''
        if context is None:
            context = {}
        ctx = context.copy()
        result = {i: False for i in ids}

        partner_id = self._get_partner(cr, uid, context=context)

        ctx['field_main_object'] = \
            self._get_main_object(cr, uid, ids, context=ctx)
        for dl_id in ids:
            subscribed_ids = self.get_complex_distribution_list_ids(
                cr, SUPERUSER_ID, [dl_id], context=ctx)[0]
            result[dl_id] = partner_id in subscribed_ids

        return result

    _inherit = "distribution.list"

    _columns = {
        'is_subscribed': fields.function(
            _compute_subscribe, string='Is subscribe', type='boolean',
            store=False),
    }

    def subscribe_to_newsletter(self, cr, uid, ids, context=None):
        '''
        Add partner of the user into the opt-in ids of the
        current distribution list
        '''
        self._update_opt(cr, uid, ids, 'in', context=context)

    def unsubscribe_to_newsletter(self, cr, uid, ids, context=None):
        '''
        Add partner of the user into the opt-out ids of the
        current distribution list
        '''
        self._update_opt(cr, uid, ids, 'out', context=context)

    def update_opt(
            self, cr, uid, dl_id, partner_ids, mode='out', context=None):
        res = super(distribution_list, self).update_opt(
            cr, uid, dl_id, partner_ids, mode=mode, context=context)
        if res and mode == 'in':
            opt_out_ids = self.read(cr, uid, dl_id, ['opt_out_ids'],
                                    context=context)['opt_out_ids']
            vals = {
                'opt_out_ids': []
            }
            for del_opt_out in list(set(partner_ids) & set(opt_out_ids)):
                vals['opt_out_ids'].append((3, del_opt_out))
            if vals['opt_out_ids']:
                self.write(cr, uid, [dl_id], vals, context=context)
        return res
