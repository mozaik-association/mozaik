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


class change_main_coordinate(orm.TransientModel):

    _name = 'change.main.coordinate'
    _description = 'Change Main Coordinate Wizard'

    _columns = {
        'invalidate_previous_coordinate': fields.boolean('Invalidate Previous Main Coordinate'),
    }

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

        partner_ids = context.get('active_ids', False) if context.get('active_ids', False) else list(context.get('res_id', False))
        if not partner_ids:
            raise orm.except_orm(_('Error'), _('At least one partner is required to change its main coordinate!'))

        wizard = self.browse(cr, uid, ids, context=context)[0]
        coord_obj = self.pool[context.get('target_model')]
        coordinate_field = coord_obj._discriminant_field
        coordinate_value = isinstance(coord_obj._columns[coordinate_field], fields.many2one) and wizard[coordinate_field].id or wizard[coordinate_field]

        context['invalidate'] = wizard.invalidate_previous_coordinate
        coord_obj.change_main_coordinate(cr, uid, partner_ids, coordinate_value, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
