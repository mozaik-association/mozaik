# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MembershipRequestOrigin(models.Model):
    _name = "membership.request.origin"
    _description = "Membership Request Origin"
    _inherit = ["mozaik.abstract.model"]
    _unicity_keys = "name"

    name = fields.Char(required=True, translate=True)
    restrict_delete = fields.Boolean()

    def unlink(self):
        if any(self.mapped("restrict_delete")):
            raise UserError(_("You cannot delete this 'Membership Request Origin'"))
        return super().unlink()
