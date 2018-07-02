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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from .res_partner import AVAILABLE_PARTNER_KINDS


class postal_coordinate(orm.Model):

    _name = 'postal.coordinate'
    _inherit = ['sub.abstract.coordinate', 'postal.coordinate']

    def _update_partner_int_instance(self, cr, uid, ids, context=None):
        """
        Update instance of partner linked to the postal coordinate case where
        coordinate is main and `active` field has same value than
        `partner.active`
        Instance is the default one if no instance for the postal coordinate
        otherwise it is its instance
        """
        for pc in self.browse(cr, uid, ids, context=context):
            # if coordinate is main update int_instance of partner
            if pc.is_main and pc.active == pc.partner_id.active and \
                    pc.partner_id.membership_state_id:
                partner = pc.partner_id
                cur_int_instance_id = partner.int_instance_id.id
                def_int_instance_id = self.pool['int.instance'].\
                    get_default(cr, uid)
                # get instance_id of address or keep default otherwise
                zip_id = pc.address_id.address_local_zip_id
                new_int_instance_id = \
                    zip_id and zip_id.int_instance_id.id or \
                    def_int_instance_id

                if new_int_instance_id != cur_int_instance_id:
                    partner_obj = self.pool['res.partner']
                    partner_obj._change_instance(
                        cr, uid, partner.id, new_int_instance_id,
                        context=context)

    _update_track = {
        'is_main': {
            'mozaik_membership.main_address_id_notification':
                lambda self, cr, uid, obj, ctx=None: obj.is_main,
            'mozaik_membership.former_address_id_notification':
                lambda self, cr, uid, obj, ctx=None: not obj.is_main,
        },
        'expire_date': {
            'mozaik_membership.former_address_id_notification':
                lambda self, cr, uid, obj, ctx=None: obj.expire_date,
        },
    }

    _int_instance_store_trigger = {
        'postal.coordinate': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['postal.coordinate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _partner_kind_store_trigger = {
        'postal.coordinate': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['postal.coordinate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        [
                            'is_assembly', 'is_company',
                            'identifier', 'membership_state_id'
                        ], 12),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
        'partner_kind': fields.related(
            'partner_id', 'kind', string='Partner Kind',
            type='selection', selection=AVAILABLE_PARTNER_KINDS,
            store=_partner_kind_store_trigger),
    }

    def write(self, cr, uid, ids, vals, context=None):
        '''
        call `_update_partner_int_instance` if `is_main` is True
        '''
        not_main_ids = self.search(
            cr, uid, [('is_main', '=', False),
                      ('id', 'in', ids)],
            context=context)
        res = super(postal_coordinate, self).write(
            cr, uid, ids, vals, not_main_ids=not_main_ids, context=context)
        if vals.get('is_main', False):
            self._update_partner_int_instance(cr, uid, ids, context=context)
            self.update_notify_followers(
                cr, uid, vals, not_main_ids, ids=ids, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        '''
        call `_update_partner_int_instance` if `is_main` is True
        '''
        context = context or {}
        change_instance = not context.get('keep_current_instance')
        ctx = dict(context, delay_notification=change_instance)
        res = super(postal_coordinate, self).create(
            cr, uid, vals, context=ctx)
        if vals.get('is_main') and change_instance:
            self._update_partner_int_instance(
                cr, uid, [res], context=context)
            self.update_notify_followers(
                cr, uid, vals, [res], context=context)
        return res
