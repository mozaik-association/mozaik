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
                # get instance_id of address or keep default if Not
                zip_id = pc.address_id.address_local_zip_id
                new_int_instance_id = \
                    zip_id and zip_id.int_instance_id.id or \
                    def_int_instance_id
                vals = {
                    'int_instance_id': new_int_instance_id,
                }
                pc.partner_id.write(vals)

                # have to create a membership lines
                partner_obj = self.pool['res.partner']
                if new_int_instance_id != cur_int_instance_id:
                    partner_obj.update_membership_line(
                        cr, uid, [partner.id], context=context)

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
        res = super(postal_coordinate, self).create(
            cr, uid, vals, context=context)
        if vals.get('is_main', False):
            if not context.get('keep_current_instance'):
                self._update_partner_int_instance(
                    cr, uid, [res], context=context)
                self.update_notify_followers(
                    cr, uid, vals, [res], context=context)
        return res
