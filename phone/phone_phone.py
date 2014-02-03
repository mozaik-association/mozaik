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
from openerp.addons.ficep_base.controller import main as fb

import phonenumbers as pn

"""
# Available Type for 'phone.phone':
# Mobile Phone - Phone - Fax
"""
AVAILABLE_TYPE = [('mobile phone', 'Mobile Phone'),
                  ('phone', 'Phone'),
                  ('fax', 'Fax')]


class phone_phone(orm.Model):

    def _check_and_format_number(self, vals, num, code):
        try:
            normalized_number = pn.parse(num, code)
        except pn.NumberParseException, e:
            raise orm.except_orm(_('Warning!'), _('Invalid phone number: %s') % _(e))

        vals['national_number'] = normalized_number.national_number
        vals['prefix'] = normalized_number.country_code
        vals['name'] = pn.format_number(normalized_number, pn.PhoneNumberFormat.INTERNATIONAL)
        return vals

    def _get_country_code(self, cr, uid, country_id, context=None):
        if context is None:
            context= {}
        return self.pool.get('res.country').read(cr, uid, country_id, ['code'], context=context)['code']

    _name = 'phone.phone'
    _columns = {
                'name': fields.char('Number', required=True, size=50, help="Exemple: 0476552611"),
                'type': fields.selection(AVAILABLE_TYPE, 'Type'),
                'country_id': fields.many2one('res.country', 'Country', required=True),
                'national_number' : fields.char('National Number', size=50),
                'prefix' : fields.char('Prefix', size=10),
                'phone_coordinate_ids': fields.one2many('phone.coordinate', 'phone_id', 'Phone Coordinate'),
                }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        country_code = self._get_country_code(cr, uid, vals['country_id'], context=context)
        vals = self._check_and_format_number(vals, vals['name'], country_code)
        return super(phone_phone, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        num = vals.get('name', False)
        country_id = vals.get('country_id', False)
        code = False if not country_id else self._get_country_code(cr, uid, country_id, context=context)
        if num != False or code != False:
            prefix = False
            to_read = []
            to_read.append('prefix')
            if not num:
                to_read.append('national_number')
            if not code:
                to_read.append('country_id')
            stored_value = self.read(cr, uid, ids, to_read, context=context)[0]
            num = num or stored_value.get('national_number')
            code = code or self._get_country_code(cr, uid, stored_value.get('country_id')[0], context=context)
            prefix = prefix or stored_value.get('prefix',False)
            num = num.replace('+%s' % prefix ,'') if prefix else num
            vals = self._check_and_format_number(vals, num, code)
        return super(phone_phone, self).write(cr, uid, ids, vals, context=context)

class phone_coordinate(orm.Model):

    _name = 'phone.coordinate'
    _rec_name = 'phone_id'
    _columns = {
                'phone_id': fields.many2one('phone.phone', string='Phone', required=True),
                'is_main': fields.boolean('Is Main'),
                'state': fields.selection(fb.AVAILABLE_PC_STATE, 'State'),
                'partner_id': fields.many2one('res.partner', 'Contact', required=True),
                'phone_type': fields.related('phone_id', 'type', type='many2one', relation='phone.phone', string='Phone Type'),
                'start_date': fields.date('Start Date'),
                'end_date': fields.date('End Date'),
                'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category'),
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
