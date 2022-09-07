# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = "res.partner.relation.all"

    this_partner_interest_group_ids = fields.Many2many(
        comodel_name="interest.group",
        string="This Partner Interest Groups",
        related="this_partner_id.interest_group_ids",
        readonly=True,
    )

    other_partner_interest_group_ids = fields.Many2many(
        comodel_name="interest.group",
        string="Other Partner Interest Groups",
        related="other_partner_id.interest_group_ids",
        readonly=True,
    )
