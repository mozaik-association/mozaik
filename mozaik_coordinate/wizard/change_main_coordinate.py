# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class change_main_coordinate(orm.TransientModel):

    _name = 'change.main.coordinate'
    _description = 'Change Main Coordinate Wizard'

    _columns = {
        'invalidate_previous_coordinate':
            fields.boolean('Invalidate Previous Main Coordinate'),
        'change_allowed':
            fields.boolean(string='Change Allowed'),
    }

    _defaults = {
        'change_allowed': True
    }

    def _switch_context(self, cr, uid, model, res_id, context=None):
        context = context or {}
        coord = self.pool.get(model).browse(cr, uid, res_id, context=context)
        context['active_model'] = 'res.partner'
        context['active_id'] = coord.partner_id.id
        context['res_id'] = [coord.partner_id.id]
        context.pop('active_ids', False)
        context['target_id'] = coord.id

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = {}
        res['change_allowed'] = True
        context = context or {}
        if not context.get('target_model'):
            raise orm.except_orm(_('Error'), _('Target model not specified!'))

        model = context.get('active_model', False)
        mode = context.get('mode', 'new')

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        if mode == 'switch':
            # switch of a main coordinate to another existing coordinate
            if not len(ids) == 1:
                raise orm.except_orm(
                    _('Error'),
                    _('Please select only one coordinate!'))
            self._switch_context(cr, uid, model, ids[0], context=context)

        return res

    def button_change_main_coordinate(self, cr, uid, ids, context=None):
        """
        =============================
        button_change_main_coordinate
        =============================
        Change main coordinate for a list of partners
        * a new main coordinate is created for each partner
        * the previsous main coordinate is invalidates or not regarding
          the option ``invalidate_previous_coordinate``
        :raise: ERROR if no partner selected

        **Note**
        When launched from the partner form the partner id is taken ``res_id``
        """
        context = context or {}
        if not context.get('target_model'):
            raise orm.except_orm(_('Error'), _('Target model not specified!'))
        mode = context.get('mode', 'new')
        model = context.get('active_model', False)
        if mode == 'switch':
            # switch of a main coordinate to another existing coordinate
            coord_ids = context.get('active_ids') \
                or (context.get('active_id') and [context.get('active_id')]) \
                or []
            self._switch_context(cr, uid, model, coord_ids[0], context=context)

        partner_ids = context.get('active_ids') if context.get(
            'active_ids') else list(context.get('res_id'))
        if not partner_ids:
            raise orm.except_orm(
                _('Error'),
                _('At least one partner is required to change its '
                  'main coordinate!'))

        wizard = self.browse(cr, uid, ids, context=context)[0]
        coord_obj = self.pool[context.get('target_model')]
        coordinate_field = coord_obj._discriminant_field
        coordinate_value = coord_obj._is_discriminant_m2o() and \
            wizard[coordinate_field].id or wizard[coordinate_field]

        context['invalidate'] = wizard.invalidate_previous_coordinate
        coord_obj.change_main_coordinate(
            cr, uid, partner_ids, coordinate_value, context=context)
