# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

    is_donor = fields.Boolean(
        string="Is a donor",
        compute='_compute_involvement_bools', store=True,
        compute_sudo=True)
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
        compute='_compute_involvement_bools', store=True,
        compute_sudo=True)

    @api.multi
    @api.depends(
        'partner_involvement_ids',
        'partner_involvement_ids.active',
        'partner_involvement_inactive_ids',
        'partner_involvement_inactive_ids.active',
    )
    def _compute_involvement_bools(self):
        for partner in self:
            types = partner.partner_involvement_ids.mapped('involvement_type')
            partner.is_donor = 'donation' in types
            partner.is_volunteer = 'voluntary' in types
