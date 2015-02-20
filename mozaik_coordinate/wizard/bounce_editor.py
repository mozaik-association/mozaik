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
from datetime import datetime

from openerp.osv import orm, fields
from openerp.tools.translate import _


class bounce_editor(orm.TransientModel):

    _name = 'bounce.editor'
    _description = 'Bounce Editor'

    _columns = {
        'increase': fields.integer('Increase by', required=True),
        'description': fields.text('Description', required=True),
        'model': fields.char('Model', required=True),
    }

    _defaults = {
        'increase': 1,
    }

# constraints

    _sql_constraints = [
        ('increase_check', 'CHECK(increase > 0)', '"increase" field should be a positive value'),
    ]

# orm methods

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if view_type == 'form':
            context = context or {}

            if not context.get('active_model', False):
                raise orm.except_orm(_('Error'), _('Missing active_model in context!'))

            if not context.get('active_ids', False):
                raise orm.except_orm(_('Error'), _('Missing active_ids in context!'))

            document_ids = context.get('active_ids')

            ids = self.pool[context['active_model']].search(cr, uid, [('id', 'in', document_ids), ('active', '=', False)], context=context)
            if ids:
                raise orm.except_orm(_('Error'), _('This action is not allowed on inactive documents!'))

        res = super(bounce_editor, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

# public methods

    def update_bounce_datas(self, cr, uid, ids, context=None):
        """
        ===================
        update_bounce_datas
        ===================
        Update the bounce information of coordinate.
        ``ids`` of the coordinate is contained into the active_ids of the context.
        """
        res_ids = context.get('active_ids', False)
        if not res_ids:
            return
        for wiz in self.browse(cr, uid, ids, context=context):
            vals = {
                'bounce_description': wiz.description,
                'bounce_date': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            }
            active_model = self.pool[wiz.model]
            coordinate_values = active_model.read(cr, uid, res_ids, ['bounce_counter'], context=context)
            for coordinate_value in coordinate_values:
                bounce_counter = coordinate_value['bounce_counter']
                vals.update({
                    'bounce_counter': bounce_counter + wiz.increase,
                })
                active_model.write(cr, uid, [coordinate_value['id']], vals, context=context)

