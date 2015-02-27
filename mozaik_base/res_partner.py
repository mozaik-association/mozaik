# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class res_partner(orm.Model):

    _inherit = 'res.partner'

    # Do not launch workflow if not yet ready for
    _enable_wkf = False

# orm methods

    def create_workflow(self, cr, uid, ids, context=None):
        """
        Do not launch workflow if not yet ready for
        """
        if self._enable_wkf:
            return super(res_partner, self).create_workflow(
                cr, uid, ids, context=context)
        return True
