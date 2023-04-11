# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MembershipLine(models.Model):

    _inherit = "membership.line"

    is_sponsored = fields.Boolean(copy=False)
