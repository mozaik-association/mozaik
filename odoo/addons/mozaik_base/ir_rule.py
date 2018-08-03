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

import openerp.tools as tools
from openerp.osv import orm


class ir_rule(orm.Model):

    _inherit = 'ir.rule'

    @tools.ormcache()
    def _compute_domain(self, cr, uid, model_name, mode="read"):
        '''
        Transform domain ('x', 'child_of', []) always evaluated to True (!)
        to the False domain
        '''
        dom = super(ir_rule, self)._compute_domain(
            cr, uid, model_name, mode=mode)
        if dom:
            dom = isinstance(dom, list) and dom or list(dom)
            ind = 0
            for d in dom:
                if not isinstance(d, str) and len(d) == 3:
                    if d[1] == 'child_of' and not d[2]:
                        dom[ind] = (0, '=', 1)
                ind += 1
        return dom

    def clear_cache(self, cr, uid):
        super(ir_rule, self)._compute_domain.clear_cache(self)
        self._compute_domain.clear_cache(self)
