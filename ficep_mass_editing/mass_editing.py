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
from openerp.osv import orm


class mass_object(orm.Model):
    _inherit = "mass.object"

    def create_action(self, cr, uid, ids, context=None):
        """
        =============
        create_action
        =============
        For All Actions Created, Disable it into the form view by
        adding True into the field ``multi``
        """
        res = super(mass_object, self).create_action(cr, uid, ids, context=context)
        rec_mass_objects = self.browse(cr, uid, ids, context=context)
        for rec_mass_object in rec_mass_objects:
            action_obj = self.pool.get('ir.actions.act_window')
            action_obj.write(cr, uid, rec_mass_object.ref_ir_act_window.id, {'multi': True}, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
