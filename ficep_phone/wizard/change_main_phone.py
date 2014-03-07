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


class change_main_phone(orm.TransientModel):

    _name = 'change.main.phone'
    _description = 'Change Main Phone Wizard'

    _columns = {
        'phone_id': fields.many2one('phone.phone', 'New Main Phone', required=True),
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
        rec_wizard = self.browse(cr, uid, ids, context=context)[0]
        context['invalidate'] = rec_wizard.invalidate_previous_coordinate
        partner_ids = context.get('active_ids', False) if context.get('active_ids', False) else list(context.get('res_id', False))
        if partner_ids:
            self.pool.get('phone.coordinate').change_main_coordinate(cr, uid, partner_ids, rec_wizard.phone_id.id, context=context)
        else:
            raise orm.except_orm(_('Error'), _('At least one partner is required to change its main coordinate!'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
