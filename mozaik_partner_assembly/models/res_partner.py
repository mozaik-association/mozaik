# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    is_assembly = fields.Boolean(
        'Is an Assembly',
        default=False,
    )

    @api.constrains('is_company', 'is_assembly')
    def _check_is_assembly(self):
        """
        Check if these two flags are consistents.
        """
        assemblies = self.filtered(lambda s: s.is_assembly)
        if not all(assemblies.mapped('is_company')):
            raise exceptions.ValidationError(
                _('An assembly must be a company'))
