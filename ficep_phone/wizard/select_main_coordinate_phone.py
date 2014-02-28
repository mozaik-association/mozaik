# -*- coding: utf-8 -*-
#
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
#

from openerp.osv import orm, fields
from openerp.tools.translate import _


class phone_main_number_change(orm.TransientModel):

    _name = 'phone.change.main.number'
    _description = 'Change Main Phone Number Wizard'

    _columns = {
        'phone_id': fields.many2one('phone.phone', 'New Main Phone', required=True),
        'invalidate_previous_phone_coordinate': fields.boolean('Invalidate Previous Main Coordinate'),
    }

    def change_main_phone_number(self, cr, uid, ids, context=None):
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
        partner_ids = context.get('active_ids', False) if context.get('active_ids', False) else list(context.get('res_id', False))
        if partner_ids:
            self.pool.get('phone.coordinate').change_main_phone_number(cr, uid, partner_ids, rec_wizard.phone_id.id, context=context)
        else:
            raise orm.except_orm(_('Error'), _('At least one partner is required to set its main phone coordinate!'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
