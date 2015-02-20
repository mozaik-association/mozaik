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

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _


class event_event(orm.Model):

    _name = "event.event"
    _inherit = ['event.event', 'mozaik.abstract.model']
    _description = "Event"

    _columns = {
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance',
            required=True, select=True, track_visibility='onchange'),
        'postal_coordinate_id': fields.many2one(
            'postal.coordinate', string='Location',
            track_visibility='onchange'),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool.get('int.instance').get_default(cr, uid),
    }

# constraints

    _unicity_keys = 'int_instance_id, name'

# orm methods

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('int_instance_id', False):
            er_ids = []
            for event in self.browse(cr, uid, ids, context=context):
                er_ids += [reg.id for reg in event.registration_ids]
            ia_obj = self.pool['int.assembly']
            follower_ids = ia_obj.get_followers_assemblies(
                cr, uid, event.int_instance_id.id, context=context)
            f_vals = [(6, 0, follower_ids)]
            reg_vals = {
                'message_follower_ids': f_vals,
            }
            er_obj = self.pool['event.registration']
            er_obj.write(cr, uid, er_ids, reg_vals, context=context)
        return super(event_event, self).write(
            cr, uid, ids, vals, context=context)

    def button_confirm(self, cr, uid, ids, context=None):
        for event in self.browse(cr, uid, ids, context=context):
            if event.seats_min > event.seats_used:
                raise orm.except_orm(_('Error'), _('Number of seats is not'
                                                   ' reached'))
        return super(event_event, self).button_confirm(
            cr, uid, ids, context=context)


class event_registration(orm.Model):

    _name = "event.registration"
    _inherit = ['event.registration', 'mozaik.abstract.model']
    _description = "Event Registration"

# private methods

    def _get_coordinates(self, cr, uid, vals, context=None):
        '''
        if `partner_id`` in vals then set `email' and `phone` with
        email coordinate and phone.coordinate of the partner
        '''
        r_fields = ['email_coordinate_id', 'mobile_coordinate_id',
                    'fix_coordinate_id', 'display_name']
        p_obj = self.pool['res.partner']
        p_id = vals['partner_id']

        p_value = p_obj.read(cr, uid, p_id, r_fields, context=context)
        vals['name'] = p_value['display_name']
        # select mobile id or fix id of no phone
        phone_id = p_value['mobile_coordinate_id'] and \
            p_value['mobile_coordinate_id'][0] or \
            p_value['fix_coordinate_id'] and \
            p_value['fix_coordinate_id'][0] or False
        if phone_id:
            ph_obj = self.pool['phone.coordinate']
            vals['phone'] = ph_obj.browse(
                cr, uid, phone_id, context=context).phone_id.name
        email_id = p_value['email_coordinate_id'] and \
            p_value['email_coordinate_id'][0] or False
        if email_id:
            e_obj = self.pool['email.coordinate']
            vals['email'] = e_obj.read(
                cr, uid, email_id, ['email'],
                context=context)['email']
            vals['email_coordinate_id'] = email_id

# constraints

    _int_instance_store_trigger = {
        'event.registration': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['event.registration'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'email_coordinate_id': fields.many2one(
            'email.coordinate', string='Email Coordinate'),
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }

    _unicity_keys = 'event_id, partner_id'

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        recompute email and phone field
        '''
        if vals.get('event_id', False):
            event = self.pool['event.event'].browse(
                cr, uid, vals['event_id'], context=context)
            if event.int_instance_id:
                ia_obj = self.pool['int.assembly']
                followers_ids = ia_obj.get_followers_assemblies(
                    cr, uid, event.int_instance_id.id, context=context)
                vals['message_follower_ids'] = [(6, 0, followers_ids)]
        if vals.get('partner_id', False):
            self._get_coordinates(cr, uid, vals, context=context)
        return super(event_registration, self).create(
            cr, uid, vals, context=context)

# public methods

    def update_coordinates(self, cr, uid, reg_id, context=None):
        reg_vals = self.read(cr, uid, reg_id, ['partner_id'])
        partner_id = reg_vals['partner_id'][0]
        vals = {
            'partner_id': partner_id,
        }
        self._get_coordinates(cr, uid, vals, context=context)
        return self.write(cr, uid, reg_id, vals, context=context)

    def button_reg_cancel(self, cr, uid, ids, context=None):
        '''
        deactivate registration if canceled
        '''
        res = super(event_registration, self).button_reg_cancel(
            cr, uid, ids, context=context)
        self.action_invalidate(cr, uid, ids, context=context)

        return res
