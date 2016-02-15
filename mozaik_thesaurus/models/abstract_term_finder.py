# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_thesaurus, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_thesaurus is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_thesaurus is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_thesaurus.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models
from __builtin__ import int


class AbstractTermFinder(models.AbstractModel):

    _name = 'abstract.term.finder'
    _description = 'Abstract Term Finder'
    _terms = []

    def search(self, cr, user, args,
               offset=0, limit=None, order=None, context=None, count=False):
        if self._terms:
            args = [[
                arg[0], 'in', self.pool['thesaurus.term'].browse(
                    cr, user, arg[2], context=context).get_children_term()
                ] if hasattr(arg, '__iter__') and arg[0] in self._terms and
                isinstance(arg[2], int) else arg for arg in args
            ]
        return super(AbstractTermFinder, self).search(
            cr, user, args,
            offset=offset, limit=limit, order=order,
            context=context, count=count)
