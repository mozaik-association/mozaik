# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassMembershipRenew(models.TransientModel):

    _name = 'mass.membership.close'
    _description = 'Former member in mass the memberships'

    date_from = fields.Date(
        required=True,
        help="End date of membership lines to close",
    )

    def doit(self):
        self.ensure_one()
        self.env["membership.line"]._launch_former_member(date_from=self.date_from)
