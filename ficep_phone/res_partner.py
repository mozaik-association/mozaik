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

from .phone_phone import phone_phone, phone_coordinate

def _get_phone_dictionary(value):
    """
    =====================
    _get_phone_dictionary
    =====================
    This method will return a dictionary using by field.function concerning
    phone coordinate
    :param value: set search_on with this value. (fix-fax-mobile)
    :type value: char
    :rparam: dictionary with needed value for ``_get_real_value``
    :rtype: {}
    """
    return {'field': '%s_coordinate_id' % value,
            'field_to_search': 'phone_type',
            'model': 'phone.coordinate',
            'target_value': 'phone_id',
            'search_on': value}


class res_partner(orm.Model):

    _inherit = "res.partner"

    def _get_real_value(self, cr, uid, ids, name, args, context=None):
        """
        ===============
        _get_real_value
        ===============
        This method will update native field of the res_partner model with the value
        of a new custom field according to support backward compatibility.
        :param name: Field that call this method
        :type name: char
        :param args: argument declared as ``arg`` into the definition of the field
                     args contains key ``field`` : the related field of
                                                   the older one ``name``
                                    ``search_on``: make search on this
                                    ``field_to_search``: field to apply search_on
                                    ``model``: the concerning model
                                    ``target_value``: the value to associate with id
        :type args: dict
        :rparam: dictionary composing by id of partner and the associated value
                 for the field ``name``
        :rtype: dict {id:value,id:value,}
        """
        res = {}.fromkeys(ids, False)
        model = self.pool.get(args['model'])
        search_list = [(args['field_to_search'], '=', args['search_on'])] if 'search_on' in args else []
        for partner_value in self.read(cr, uid, ids, [args['field']], context=context):
            record_id = model.search(cr, uid,
                [('partner_id', '=', partner_value['id']),
                 ('is_main', '=', True),
                 ('expire_date', '=', False)] + search_list,
                context=context)
            # record_id must always be true with this expression len(record_id)==1 otherwise take the first
            if record_id:
                res[partner_value['id']] = model.read(cr, uid, record_id[0], [args['target_value']], context=context)[args['target_value']][1]
            else:
                res[partner_value['id']] = partner_value[args['field']][1] if partner_value[args['field']] else partner_value[args['field']]
        return res

    _columns = {
        'phone_coordinate_ids': fields.one2many('phone.coordinate', 'partner_id', 'Phone Coordinates'),
        'fix_coordinate_id': fields.many2one('phone.coordinate', 'Phone Coordinate', readonly=True,
                                             domain=['&', ('is_main', '=', True), ('phone_type', '=', 'fix')]),
        'mobile_coordinate_id': fields.many2one('phone.coordinate', 'Mobile Coordinate', readonly=True,
                                             domain=['&', ('is_main', '=', True), ('phone_type', '=', 'mobile')]),
        'fax_coordinate_id': fields.many2one('phone.coordinate', 'Fax Coordinate', readonly=True,
                                             domain=['&', ('is_main', '=', True), ('phone_type', '=', 'fax')]),

        # This will allow to continue to feed native fields of OpenERP for backward compatibility
        'phone': fields.function(_get_real_value, arg=_get_phone_dictionary('fix'), string='Phone',
                                 type='char', relation="phone.coordinate",
                                 store={
                                        'phone.coordinate': (phone_coordinate.get_linked_partners, ['phone_id'], 10),
                                        'phone.phone': (phone_phone.get_linked_partners, ['name','type'], 10),
                                       },
                                ),
        'fax': fields.function(_get_real_value, arg=_get_phone_dictionary('fax'), string='Fax',
                                 type='char', relation="phone.coordinate",
                                 store={
                                        'phone.coordinate': (phone_coordinate.get_linked_partners, ['phone_id'], 10),
                                        'phone.phone': (phone_phone.get_linked_partners, ['name','type'], 10),
                                       },
                                ),
        'mobile': fields.function(_get_real_value, arg=_get_phone_dictionary('mobile'), string='Mobile',
                                 type='char', relation="phone.coordinate",
                                 store={
                                        'phone.coordinate': (phone_coordinate.get_linked_partners, ['phone_id'], 10),
                                        'phone.phone': (phone_phone.get_linked_partners, ['name','type'], 10),
                                       },
                                ),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
