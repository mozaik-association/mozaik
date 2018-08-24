# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    usual_firstname = fields.Char()
    usual_lastname = fields.Char()
    usual_name = fields.Char(
        compute='_compute_usual_name',
        store=True,
        index=True,
    )

    @api.multi
    def _get_names(self, reverse=False, usual=False):
        """
        Return firstname and lastname in an iterable for one partner
        using usual_* fields if any
        Optionaly the result can be reversed
        """
        names = [
            usual and self.usual_lastname or self.lastname or '',
            usual and self.usual_firstname or self.firstname or '',
        ]
        if reverse:
            names = list(reversed(names))
        return names

    @api.multi
    @api.depends(
        'is_company',
        'firstname', 'lastname', 'usual_firstname', 'usual_lastname')
    def _compute_usual_name(self):
        """
        Compute selected names from all available names
        """
        for partner in self:
            if partner.is_company:
                u_name = partner.name
            else:
                names = partner._get_names(usual=True)
                u_name = partner._get_computed_name(
                    names[0], names[1])

            partner.usual_name = u_name

    @api.multi
    def _sanitize_names(self):
        """
        Coerce *name and usual_*name
        """
        for p in self:
            vals = {}
            if not p.lastname and p.usual_lastname:
                vals['lastname'] = p.usual_lastname
                vals['usual_lastname'] = False
            if p.lastname == p.usual_lastname:
                vals['usual_lastname'] = False
            if not p.firstname and p.usual_firstname:
                vals['firstname'] = p.usual_firstname
                vals['usual_firstname'] = False
            if p.firstname == p.usual_firstname:
                vals['usual_firstname'] = False
            if vals:
                p.write(vals)

    @api.model
    def create(self, values):
        """
        Sanitize names after create()
        """
        res = super().create(values)
        res.with_context(escape_sanitize=True)._sanitize_names()
        return res

    @api.multi
    def write(self, values):
        """
        Sanitize names after write()
        """
        res = super().write(values)
        if not self._context.get('escape_sanitize'):
            self.with_context(escape_sanitize=True)._sanitize_names()
        return res
