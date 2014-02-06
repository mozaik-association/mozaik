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
import phonenumbers as pn

from openerp.osv import orm, fields
from openerp.tools.translate import _

from openerp.addons.ficep_base.controller.main import Controller as Ctrl


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
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
                'id': fields.integer('ID', readonly=True),
                'name': fields.char('Number', required=True, size=50),
                'type': fields.selection(AVAILABLE_TYPE, 'Type', required=True),
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
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'phone_id'

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'phone_id': fields.many2one('phone.phone', string='Phone', required=True),
        'is_main': fields.boolean('Is Main'),
        'phone_type': fields.related('phone_id', 'type', type='selection', string='Phone Type',
                                      relation='phone.phone', selection=AVAILABLE_TYPE, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Contact', required=True,),
        'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category'),
        'create_date': fields.date('Creation Date'),
        'expire_date': fields.date('Expiration Date'),
        'active': fields.boolean('Active'),
    }

    def check_at_least_one_main(self, cr, uid, ids, context=None):
        """
        That constraint will check the associated partner has at least one main
        coordinate if this one isn't it
        """
        context = context or {}
        phone_coordinate = self.browse(cr, uid, ids, context=context)[0]
        if phone_coordinate.phone_type == 'phone':
            if not phone_coordinate.partner_id.phone_coordinate_id and not phone_coordinate.is_main:
                return False
        else:
            if not phone_coordinate.partner_id.mobile_phone_coordinate_id and not phone_coordinate.is_main:
                return False
        return True

    _defaults = {
        'active': True
    }

    _constraints = [
        (check_at_least_one_main, _('Error! At least one main coordinate by associated partner'), ['partner_id']),
    ]

    def create(self, cr, uid, vals, context=None):
        """
        Create a coordinate phone:
        When 'is_main' is true the coordinate has to become the main coordinate for its
        associated partner.
        That implies to remove the current-valid-main coordinate by calling the
        'check_unicity_main' of Controller.
        Next step is to replicate (ref. spec.) the new coordinate into the related partner
        In the end call super create
        """
        context = context or {}
        if vals.get('is_main', False):
            ctrl = Ctrl(cr, uid, context)
            phone_type = self.pool.get('phone.phone').read(cr, uid, vals['phone_id'], ['type'], context=context)['type']
            target_domain = [('phone_type', '=', phone_type),
                             ('is_main', '=', True),
                             ('active', '=', True),
                             ('partner_id', '=', vals['partner_id'])]
            target_model = self._name
            field_to_update = 'is_main'
            value_to_set = False
            ctrl.check_unicity_main(self, target_model, target_domain, field_to_update, value_to_set)
            new_id = super(phone_coordinate, self).create(cr, uid, vals, context=context)
            model_field = 'phone_coordinate_id' if phone_type == 'phone' else 'mobile_phone_coordinate_id'
            ctrl.replicate(self, new_id, model_field)
            return new_id
        return super(phone_coordinate, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        return super(phone_coordinate, self).write(cr, uid, ids, vals, context=context)

    def invalidate(self, cr, uid, ids, context=None):
        context = context or {}
        ctrl = Ctrl(cr, uid, context)
        model_field = 'phone_coordinate_id' if self.read(cr, uid, ids, \
                      ['phone_type'], context=context) == 'phone' else 'mobile_phone_coordinate_id'
        ctrl.remove_main(self, ids, model_field)
        return self.write(cr, uid, ids, {'is_main': False,
                                         'end_date': fields.date.context_today(self, cr, uid, context=context)}, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
