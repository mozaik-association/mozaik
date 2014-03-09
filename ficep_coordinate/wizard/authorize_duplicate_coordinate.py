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
from openerp.tools import SUPERUSER_ID


class authorize_duplicate_coordinate(orm.TransientModel):

    _name = "authorize.duplicate.coordinate"

    def button_authorize_duplicate_coordinate(self, cr, uid, ids, context=None):
        if not context.get('active_model', False):
            raise orm.except_orm(_('Error'), _('Missing active_model in context action'))

        coord_obj = self.pool[context.get('active_model')]
        coordinate_field = coord_obj._coordinate_field
        coordinate_ids = context.get('active_ids')

        coordinates = coord_obj.browse(cr, uid, coordinate_ids, context=context)
        coordinate_field_ids = []
        for coordinate in coordinates:
            if not coordinate['is_duplicate_detected']:
                raise orm.except_orm(_('Error'), _('Only duplicated coordinates are allowed!'))
            coordinate_field_ids.append(coordinate[coordinate_field])

        if len(set(coordinate_field_ids)) != 1:
            raise orm.except_orm(_('Error'), _('Only duplicated coordinates related to the same "%s" are allowed!') % coord_obj._columns[coordinate_field].string)

        if len(coordinate_ids) == 1:
            # can now search all for this type of coordinate: coordinate field is the same
            value = isinstance(coord_obj._columns[coord_obj._coordinate_field], fields.many2one) and coordinate_field_ids[0].id or coordinate_field_ids[0]
            allowed_coordinate_ids = coord_obj.search(cr, SUPERUSER_ID, [(coordinate_field, '=', value),
                                                                         ('is_duplicate_allowed', '=', True)], context=context)
            if not allowed_coordinate_ids:
                raise orm.except_orm(_('Error'), _('You must select more than one coordinate!'))

        coord_obj.write(cr, uid, coordinate_ids, {'is_duplicate_detected': False, 'is_duplicate_allowed': True})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
