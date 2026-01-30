# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequest(models.Model):
    _inherit = "membership.request"

    origin_id = fields.Many2one(comodel_name="membership.request.origin")
