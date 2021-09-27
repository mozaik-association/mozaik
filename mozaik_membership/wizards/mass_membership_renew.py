# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassMembershipRenew(models.TransientModel):

    _name = 'mass.membership.renew'

    date_from = fields.Date(
        required=True,
        help="Start date of new membership lines",
    )

    def doit(self):
        self.ensure_one()
        self.env["membership.line"]._launch_renew(date_from=self.date_from)
