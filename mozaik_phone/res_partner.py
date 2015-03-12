# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_phone, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_phone is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_phone is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_phone.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _

# Local imports
from .phone_phone import PHONE_AVAILABLE_TYPES, phone_available_types


class res_partner(orm.Model):

    _inherit = "res.partner"

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    def _get_main_phone_coordinate_ids(
            self,
            cr,
            uid,
            ids,
            name,
            args,
            context=None):
        """
        ==============================
        _get_main_phone_coordinate_ids
        ==============================
        Reset *_coordinate_id fields with corresponding main phone coordinate
        ids
        :param ids: partner ids for which new *_coordinate_id fields have to
        be recomputed
        :type name: char
        :rparam: dictionary for all partner id with requested main coordinate
                 ids
        :rtype: dict {partner_id:{'fix_coordinate_id': main_fix_id,
                                  'mobile_coordinate_id': main_mobile_id,
                                  'fax_coordinate_id': main_fax_id,
                                 }}
        Note:
        Calling and result convention: Multiple mode
        """
        result = {i: {'%s_coordinate_id' %
                      cid[0]: False for cid in PHONE_AVAILABLE_TYPES}
                  for i in ids}
        coord_obj = self.pool['phone.coordinate']
        coordinate_ids = coord_obj.search(
            cr, uid, [
                ('partner_id', 'in', ids),
                ('is_main', '=', True),
                ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(
                cr, SUPERUSER_ID, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                if coord.phone_id.also_for_fax:
                    result[coord.partner_id.id]['fax_coordinate_id'] = coord.id
                result[
                    coord.partner_id.id][
                    '%s_coordinate_id' %
                    coord.coordinate_type] = coord.id
        return result

    def _get_main_phone_numbers(self, cr, uid, ids, name, args, context=None):
        """
        =======================
        _get_main_phone_numbers
        =======================
        Reset main phone number field for a given phone type
        :param ids: partner ids for which the phone number has to be recomputed
        :type name: char
        :rparam: dictionary for all partner ids with the requested main phone
                 number
        :rtype: dict {partner_id: main_phone_number}
        Note:
        Calling and result convention: Single mode
        """
        coordinate_type = args.get('type')
        if not coordinate_type or coordinate_type not in phone_available_types:
            raise orm.except_orm(
                _('Validate Error'),
                _('Invalid phone type: "%s"!') %
                args.get(
                    'type',
                    _('Undefined')))
        result = {i: False for i in ids}
        coord_obj = self.pool['phone.coordinate']
        if coordinate_type == 'fax':
            domain = [
                '|',
                ('coordinate_type',
                 '=',
                 'fax'),
                '&',
                ('coordinate_type',
                 '=',
                 'fix'),
                ('also_for_fax',
                 '=',
                 True)]
        else:
            domain = [('coordinate_type', '=', coordinate_type)]
        coordinate_ids = coord_obj.search(cr,
                                          SUPERUSER_ID,
                                          [('partner_id',
                                            'in',
                                            ids),
                                           ('is_main',
                                            '=',
                                            True),
                                              ('active',
                                               '<=',
                                               True)] + domain,
                                          context=context)
        for coord in coord_obj.browse(
                cr,
                SUPERUSER_ID,
                coordinate_ids,
                context=context):
            if coord.active == coord.partner_id.active:
                val = ''
                if coord.vip:
                    val = 'VIP'
                else:
                    val = coord.phone_id.name
                result[
                    coord.partner_id.id] = val
        return result

    _phone_store_triggers = {
        'phone.coordinate': (
            lambda self, cr, uid, ids, context=None:
            self.pool['phone.coordinate'].get_linked_partners(
                cr, uid, ids, context=context), [
                'partner_id', 'phone_id', 'is_main', 'vip',
                'unauthorized', 'active'], 10),
        'phone.phone': (
            lambda self, cr, uid, ids, context=None:
            self.pool['phone.phone'].get_linked_partners(
                cr, uid, ids, context=context), [
                'name', 'type', 'also_for_fax'], 10), }

    _columns = {
        'phone_coordinate_ids': fields.one2many(
            'phone.coordinate', 'partner_id', 'Phone Coordinates',
            domain=[('active', '=', True)], context={'force_recompute': True}),
        'phone_coordinate_inactive_ids': fields.one2many(
            'phone.coordinate', 'partner_id', 'Phone Coordinates',
            domain=[('active', '=', False)]),

        'fix_coordinate_id': fields.function(
            _get_main_phone_coordinate_ids, string='Phone',
            type='many2one', relation="phone.coordinate",
            multi='AllPhoneIdsInOne'),

        'mobile_coordinate_id': fields.function(
            _get_main_phone_coordinate_ids, string='Mobile',
            type='many2one', relation="phone.coordinate",
            multi='AllPhoneIdsInOne'),

        'fax_coordinate_id': fields.function(
            _get_main_phone_coordinate_ids, string='Fax',
            type='many2one', relation="phone.coordinate",
            multi='AllPhoneIdsInOne'),

        # Standard fields redefinition
        'phone': fields.function(
            _get_main_phone_numbers, arg={'type': 'fix'}, string='Phone',
            type='char', select=True, store=_phone_store_triggers),
        'mobile': fields.function(
            _get_main_phone_numbers, arg={'type': 'mobile'}, string='Mobile',
            type='char', select=True, store=_phone_store_triggers),
        'fax': fields.function(
            _get_main_phone_numbers, arg={'type': 'fax'}, string='Fax',
            type='char', select=True, store=_phone_store_triggers),
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        """
        default = default or {}
        default.update({
            'phone_coordinate_ids': [],
            'phone_coordinate_inactive_ids': [],
        })
        res = super(
            res_partner,
            self).copy_data(
            cr,
            uid,
            ids,
            default=default,
            context=context)
        return res
