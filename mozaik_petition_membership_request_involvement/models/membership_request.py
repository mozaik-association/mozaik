# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    petition_registration_id = fields.Many2one(
        comodel_name="petition.registration",
        string="Associated Petition Signatory",
        help="The membership request came from a petition signature.",
        readonly=True,
    )
