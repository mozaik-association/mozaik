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
from datetime import datetime

from openerp.osv import orm, fields


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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
