# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AbstractTermFinder(models.AbstractModel):

    _name = 'abstract.term.finder'
    _description = 'Abstract Term Finder'
    _terms = []

    @api.model
    def search(self, args,
               offset=0, limit=None, order=None, count=False):
        """
        Overide to search over through child terms of a term
        :param args: domain to modify (list) or None
        """
        if self._terms:
            domain = []
            for arg in args:
                if hasattr(arg, '__iter__') and arg[0] in self._terms and\
                        arg[1] == '=' and isinstance(arg[2], int):
                    # add term domain search
                    domain += [
                        [arg[0], 'in', self.env['thesaurus.term'].browse(
                            arg[2])._get_child_terms().ids]
                    ]
                else:
                    # default search domain
                    domain += [arg]
            args = domain
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count)
