# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class sub_abstract_coordinate(orm.AbstractModel):

    _name = 'sub.abstract.coordinate'
    _inherit = ['abstract.coordinate']

    def _update_followers(
            self, cr, uid, ids, fol_ids=False, context=None):
        '''
        Update followers list for each coordinate of the same partner
        '''
        p_obj = self.pool['res.partner']
        subtype_ids = p_obj._get_subtype_ids(
            cr, uid, self._name, context=context)
        if not fol_ids:
            c = self.browse(cr, uid, ids[0], context=context)
            fol_ids = p_obj._get_followers_assemblies(
                cr, uid, c.partner_id.id, context=context)
        self.message_subscribe(
            cr, uid, ids, fol_ids,
            subtype_ids=subtype_ids, context=context)

    def _update_notify_followers(
            self, cr, uid, ids, partner_ids, context=None):
        if context is None:
            context = {}
        if not context.get('no_update', False):
            self.pool['res.partner']._update_followers(
                cr, uid, partner_ids, context=context)
        subtype = 'mozaik_membership.main_%s_notification' %\
            self._discriminant_field
        for i in ids:
            self._message_post(
                cr, uid, i, subtype=subtype, context=context)

    _track = {}
    _update_track = {}

    _int_instance_store_trigger = {}

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }

    def write(self, cr, uid, ids, vals, not_main_ids=False, context=None):
        '''
        no update and notify follower if is_main is True
        '''
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['no_update'] = True
        res = super(sub_abstract_coordinate, self).write(
            cr, uid, ids, vals, context=context)
        self.update_notify_followers(
            cr, SUPERUSER_ID, vals, not_main_ids, ids, context=ctx)
        return res

    def create(self, cr, uid, vals, context=None):
        '''
        update and notify follower if is_main is True
        '''
        context = context or {}
        res = super(sub_abstract_coordinate, self).create(
            cr, uid, vals, context=context)
        self._update_followers(
            cr, SUPERUSER_ID, [res], context=context)
        if vals.get('is_main') and not context.get('install_mode') and \
                not context.get('delay_notification'):
            ctx = dict(context, no_update=True)
            self.update_notify_followers(
                cr, SUPERUSER_ID, vals, [res], context=ctx)
        return res

    def update_notify_followers(
            self, cr, uid, vals, not_main_ids, ids=False, context=None):
        new_main_ids = []
        if ids and not_main_ids:
            if vals.get('is_main', False):
                partner_ids = []
                # assure change is well made after write
                new_main_ids = self.search(
                    cr, uid, [('is_main', '=', True),
                              ('id', 'in', not_main_ids)],
                    context=context)
                if not vals.get('partner_id', False):
                    for pc in self.browse(
                            cr, uid, new_main_ids, context=context):
                        partner_ids.append(pc.partner_id.id)
                else:
                    partner_ids.append(vals['partner_id'])
        elif vals.get('partner_id', False):
            partner_ids = [vals['partner_id']]
            new_main_ids = not_main_ids
        if new_main_ids:
            self._update_notify_followers(
                cr, SUPERUSER_ID, new_main_ids, partner_ids, context=context)

    def _register_hook(self, cr):
        '''
        Update track dict with new values
        '''
        super(sub_abstract_coordinate, self)._register_hook(cr)
        self._track.update(self._update_track)
