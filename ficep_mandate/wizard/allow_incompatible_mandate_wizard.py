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


class allow_incompatible_mandate_wizard(orm.TransientModel):

    _inherit = "allow.duplicate.wizard"
    _name = "allow.incompatible.mandate.wizard"

    def button_allow_duplicate(self, cr, uid, ids, context=None, vals=None):
        context = context or {}
        super(allow_incompatible_mandate_wizard, self).button_allow_duplicate(cr, uid, ids, context=context, vals=vals)

        # redirect to the representative's form view
        ids = context.get('active_ids')
        generic_mandate = self.pool['generic.mandate'].read(cr, uid, ids[0], ['partner_id'], context=context)
        return self.pool.get('res.partner').display_object_in_form_view(cr, uid, generic_mandate['partner_id'][0], context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
