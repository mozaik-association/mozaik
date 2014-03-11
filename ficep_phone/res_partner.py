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
from openerp.tools.translate import _

# Local imports
from .phone_phone import PHONE_AVAILABLE_TYPES, phone_available_types


class res_partner(orm.Model):

    _inherit = "res.partner"

    def _get_linked_partners_from_coordinates(self, cr, uid, ids, context=None):
        """
        =====================================
        _get_linked_partners_from_coordinates
        =====================================
        Return partner ids linked to coordinates ids
        :param ids: triggered coordinates ids
        :type name: list
        :rparam: partner ids
        :rtype: list
        """
        coord_model = self.pool['phone.coordinate']
        return coord_model.get_linked_partners(cr, uid, ids, context=context)

    def _get_linked_partners_from_phones(self, cr, uid, ids, context=None):
        """
        ================================
        _get_linked_partners_from_phones
        ================================
        Return partner ids linked by coordinates to phone ids
        :param ids: triggered phone ids
        :type name: list
        :rparam: partner ids
        :rtype: list
        """
        phone_model = self.pool['phone.phone']
        return phone_model.get_linked_partners(cr, uid, ids, context=context)

    def _get_main_phone_coordinate_ids(self, cr, uid, ids, name, args, context=None):
        """
        ==============================
        _get_main_phone_coordinate_ids
        ==============================
        Reset *_coordinate_id fields with corresponding main phone coordinate ids
        :param ids: partner ids for which new *_coordinate_id fields have to be recomputed
        :type name: char
        :rparam: dictionary for all partner id with requested main coordinate ids
        :rtype: dict {partner_id:{'fix_coordinate_id': main_fix_id,
                                  'mobile_coordinate_id': main_mobile_id,
                                  'fax_coordinate_id': main_fax_id,
                                 }}
        Note:
        Calling and result convention: Multiple mode
        """
        result = {}.fromkeys(ids, {'%s_coordinate_id' % cid[0]: False for cid in PHONE_AVAILABLE_TYPES})
        coord_obj = self.pool['phone.coordinate']
        coordinate_ids = coord_obj.search(cr, uid, [('partner_id', 'in', ids),
                                                    ('is_main', '=', True),
                                                    ('active','<=',True)], context=context)
        for coord in coord_obj.browse(cr, uid, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id]['%s_coordinate_id' % coord.coordinate_type] = coord.id
        return result

    def _get_main_phone_numbers(self, cr, uid, ids, name, args, context=None):
        """
        =======================
        _get_main_phone_numbers
        =======================
        Reset a main phone number field for a given phone type
        :param ids: partner ids for which the phone number has to be recomputed
        :type name: char
        :rparam: dictionary for all partner ids with the requested main phone number
        :rtype: dict {partner_id: main_phone_number}
        Note:
        Calling and result convention: Single mode
        """
        coordinate_type = args.get('type')
        if not coordinate_type or coordinate_type not in phone_available_types:
            raise orm.except_orm(_('ValidateError'), _('Invalid phone type: "%s"!') % args.get('type', _('Undefined')))
        result = {}.fromkeys(ids, False)
        coord_obj = self.pool['phone.coordinate']
        coordinate_ids = coord_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids),
                                                             ('coordinate_type', '=', coordinate_type),
                                                             ('is_main', '=', True),
                                                             ('active','<=',True)], context=context)
        for coord in coord_obj.browse(cr, SUPERUSER_ID, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                result[coord.partner_id.id] = 'VIP' if coord.vip else 'N/A: %s' % coord.phone_id.name if coord.unauthorized else coord.phone_id.name
        return result

    _phone_store_triggers = {
                               'phone.coordinate': (_get_linked_partners_from_coordinates, ['partner_id', 'phone_id', 'is_main', 'vip', 'unauthorized', 'active'], 10),
                               'phone.phone': (_get_linked_partners_from_phones, ['name', 'type'], 10),
                            }

    _columns = {
        'phone_coordinate_ids': fields.one2many('phone.coordinate', 'partner_id', 'Phone Coordinates', domain=[('active', '=', True)]),
        'phone_coordinate_inactive_ids': fields.one2many('phone.coordinate', 'partner_id', 'Phone Coordinates', domain=[('active', '=', False)]),

        'fix_coordinate_id': fields.function(_get_main_phone_coordinate_ids, string='Phone',
                                             type='many2one', relation="phone.coordinate", multi='AllInOne'),

        'mobile_coordinate_id': fields.function(_get_main_phone_coordinate_ids, string='Mobile',
                                                type='many2one', relation="phone.coordinate", multi='AllInOne'),

        'fax_coordinate_id': fields.function(_get_main_phone_coordinate_ids, string='Fax',
                                             type='many2one', relation="phone.coordinate", multi='AllInOne'),

        # Standard fields redefinition
        'phone': fields.function(_get_main_phone_numbers, arg={'type': 'fix'}, string='Phone',
                                 type='char', relation="phone.coordinate", select=True,
                                 store=_phone_store_triggers,
                                ),
        'mobile': fields.function(_get_main_phone_numbers, arg={'type': 'mobile'}, string='Mobile',
                                 type='char', relation="phone.coordinate", select=True,
                                 store=_phone_store_triggers,
                                ),
        'fax': fields.function(_get_main_phone_numbers, arg={'type': 'fax'}, string='Fax',
                                 type='char', relation="phone.coordinate",
                                 store=_phone_store_triggers,
                                ),
    }

# orm methods

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default.update({'phone_coordinate_ids': []})
        res = super(res_partner, self).copy(cr, uid, ids, default=default, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        When invalidating a partner, invalidates also its phone coordinates 
        """
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals and not vals['active']:
            coord_obj = self.pool['phone.coordinate']
            coord_ids = []
            for partner in self.browse(cr, SUPERUSER_ID, ids, context=context):
                coord_ids += [c.id for c in partner.phone_coordinate_ids]
            if coord_ids:
                coord_obj.button_invalidate(cr, SUPERUSER_ID, coord_ids, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
