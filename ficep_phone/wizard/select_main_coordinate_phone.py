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


class phone_coordinate_wizard(orm.TransientModel):

    _name = 'phone.coordinate.wizard'

    def mass_select_as_main(self, cr, uid, ids, context=None):
        """
        ===================
        mass_select_as_main
        ===================
        This method provides a way to select a coordinate as main for a group
        of selected partner (context['active_ids'])
        * phone coordinate will be create for the other partner of the list
        * The previsous phone coordinate will be invalidate if the user has
            check ``invalidate_previous_phone_coordinate``
        :rparam: id or ids created
        :rtype: integer or [integer]
        :raise: ERROR if no active_id and no active_ids into the context

        **Note**
        When it is launched from the partner form then take the id into ``res_id``
        """
        context = context or {}
        rec_wizard = self.browse(cr, uid, ids, context=context)[0]
        context['invalidate'] = rec_wizard.invalidate_previous_phone_coordinate
        if context.get('active_ids', False):
            #will call create method for all partner id into the active_ids
            return [(self.pool.get('phone.coordinate').create(cr, uid, {
                                                            'phone_id': rec_wizard.phone_coordinate_id.phone_id.id,
                                                            'is_main': True,
                                                            'partner_id':_id,
                                                        }, context=context)) for _id in context.get('active_ids')]
        elif context.get('res_id', False):
            return self.pool.get('phone.coordinate').create(cr, uid, {
                                                        'phone_id': rec_wizard.phone_coordinate_id.phone_id.id,
                                                        'is_main': True,
                                                        'partner_id': context.get('res_id'),
                                                        }, context=context)
        else:
            raise orm.except_orm(_('ERROR!'), _('At Least One Partner Is Required To Select A Phone Main Coordinate'))

    _columns = {
        'phone_coordinate_id': fields.many2one('phone.coordinate', 'New Main Coordinate', required=True),
        'invalidate_previous_phone_coordinate': fields.boolean('Invalidate Previous Coordinate'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
