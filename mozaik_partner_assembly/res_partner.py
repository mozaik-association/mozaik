# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_partner_assembly, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_partner_assembly is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_partner_assembly is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_partner_assembly.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class res_partner(orm.Model):

    _inherit = 'res.partner'

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    _columns = {
        'is_assembly': fields.boolean('Is an Assembly'),
    }

    _defaults = {
        'is_assembly': False,
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Reset some fields to their initial values.
        """
        default = default or {}
        default.update({
            'is_assembly': False,
        })
        res = super(
            res_partner,
            self).copy_data(
            cr,
            uid,
            ids,
            default=default,
            context=context)
        return res
