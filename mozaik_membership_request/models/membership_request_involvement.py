# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequestInvolvement(models.Model):
    _name = "membership.request.involvement"
    _description = "Membership Request Involvement"

    def _get_involvement_category_domain(self):
        # Reuse the same domain logic from membership.request
        return self.env["membership.request"]._get_involvement_category_domain()

    membership_request_id = fields.Many2one(
        "membership.request",
        string="Membership Request",
        required=True,
        ondelete="cascade",
    )
    involvement_category_id = fields.Many2one(
        "partner.involvement.category",
        string="Involvement Category",
        required=True,
        ondelete="cascade",
        domain=lambda self: self._get_involvement_category_domain(),
    )
    note = fields.Text(string="Note")

    name = fields.Char(
        related="involvement_category_id.name",
        readonly=True,
    )
    involvement_type = fields.Selection(
        related="involvement_category_id.involvement_type",
        readonly=True,
    )
    allow_multi = fields.Boolean(
        related="involvement_category_id.allow_multi",
        readonly=True,
    )
    code = fields.Char(
        related="involvement_category_id.code",
        readonly=True,
    )
