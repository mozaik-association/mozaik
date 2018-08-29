# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class allow_incompatible_mandate_wizard(orm.TransientModel):

    _inherit = "allow.duplicate.wizard"
    _name = "allow.incompatible.mandate.wizard"

    def button_allow_duplicate(self, cr, uid, ids, context=None):
        context = context or {}
        super(allow_incompatible_mandate_wizard, self).button_allow_duplicate(
            cr, uid, ids, context=context)

        # redirect to the representative's form view
        ids = context.get('active_ids')
        generic_mandate = self.pool['generic.mandate'].read(cr,
                                                            uid,
                                                            ids[0],
                                                            ['partner_id'],
                                                            context=context)
        return self.pool['res.partner'].display_object_in_form_view(
            cr,
            uid,
            generic_mandate['partner_id'][0],
            context=context)
