# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
                    cr, user, arg[2], context=context).get_children_term().ids
                ] if hasattr(arg, '__iter__') and arg[0] in self._terms and
                arg[1] == '=' and
                isinstance(arg[2], int) else arg for arg in args
            ]
        return super(AbstractTermFinder, self).search(
            cr, user, args,
            offset=offset, limit=limit, order=order,
            context=context, count=count)
