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
from openerp.tools.translate import _
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

    def _check_positive_increase(self, cr, uid, ids, context=None):
        """
        =============
        _check_positif
        =============
        :rparam: False if ``increase`` is < 1
                 Else True
        :rtype: Boolean
        """
        for wiz in self.browse(cr, uid, ids, context=context):
            if wiz.increase < 1:
                return False
        return True

    _constraints = [
        (_check_positive_increase, _('Increase Should Be a Positive Number'), ['increase']),
    ]

# public methods

    def update_bounce_datas(self, cr, uid, ids, context=None):
        """
        ===================
        update_bounce_datas
        ===================
        """
        for wiz in self.browse(cr, uid, ids, context=context):
            res_ids = context.get('active_ids', False)
            if not res_ids:
                continue
            active_model = self.pool[wiz.model]
            coordinate_values = active_model.read(cr, uid, res_ids, ['bounce_counter'], context=context)
            for coordinate_value in coordinate_values:
                curr_bounce_counter = coordinate_value['bounce_counter']
                bounce_counter = curr_bounce_counter + wiz.increase
                active_model.write(cr, uid, [coordinate_value['id']], {'bounce_counter': bounce_counter,
                                                                       'bounce_description': wiz.description})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
