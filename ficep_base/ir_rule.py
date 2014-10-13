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
