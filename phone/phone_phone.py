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
from openerp.tools.translate import _

from openerp.addons.ficep_base.controller.main import Controller as Ctrl
from openerp.addons.ficep_base.controller.ficep_constant import *

import phonenumbers as pn

"""
# Available Type for 'phone.phone':
# Mobile Phone - Phone - Fax
"""
AVAILABLE_TYPE = [('mobile phone', 'Mobile Phone'),
                  ('phone', 'Phone'),
                  ('fax', 'Fax')]

PREFIX_NUM = 'BE'


class phone_phone(orm.Model):

    def _check_and_format_number(self, vals, num):
        code = False
        if num[:2] == '00':
            num = '%s%s' % (num[:2].replace('00', '+'), num[2:])
        else:
            code = PREFIX_NUM
        try:
            normalized_number = pn.parse(num, code) if code else pn.parse(num)
        except pn.NumberParseException, e:
            raise orm.except_orm(_('Warning!'), _('Invalid phone number: %s') % _(e))
        vals['name'] = pn.format_number(normalized_number, pn.PhoneNumberFormat.INTERNATIONAL)

    _name = 'phone.phone'
    _columns = {
                'name': fields.char('Number', required=True, size=50, help="Exemple: 0476552611"),
                'type': fields.selection(AVAILABLE_TYPE, 'Type'),
                'phone_coordinate_ids': fields.one2many('phone.coordinate', 'phone_id', 'Phone Coordinate'),
                }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        self._check_and_format_number(vals, vals['name'])
        return super(phone_phone, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        num = vals.get('name', False)
        if num:
            self._check_and_format_number(vals, num)
        return super(phone_phone, self).write(cr, uid, ids, vals, context=context)


class phone_coordinate(orm.Model):

    _name = 'phone.coordinate'
    _rec_name = 'phone_id'
    _columns = {
                'phone_id': fields.many2one('phone.phone', string='Phone', required=True),
                'is_main': fields.boolean('Is Main'),
                'state': fields.selection(AVAILABLE_PC_STATE, 'State'),
                'partner_id': fields.many2one('res.partner', 'Contact', required=True),
                'phone_type': fields.related('phone_id', 'type', type='selection', relation='phone.phone', string='Phone Type'),
                'start_date': fields.date('Start Date'),
                'end_date': fields.date('End Date'),
                'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category'),
                }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('is_main', False):
            ctrl = Ctrl(cr, uid, context)
            search_on_target = [('state', '=', 'valid'),
                                ('is_main', '=', True),
                                ('partner_id', '=', vals['partner_id'])]
            target_model = self._name
            field_to_update = 'is_main'
            ctrl.replication(self, target_model, search_on_target, field_to_update)
        new_id = super(phone_coordinate, self).create(cr, uid, vals, context=context)
        ctrl.set_partner_id(self, new_id, 'phone_coordinate_id')
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        return super(phone_coordinate, self).write(cr, uid, ids, vals, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
