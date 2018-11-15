# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class MassMembershipRenew(models.TransientModel):

    _name = 'mass.membership.renew'

    date_from = fields.Date(
        default=fields.Date.today(),
        help="Start date of new membership lines",
    )

    @api.multi
    def doit(self):
        self.ensure_one()
        self.with_delay()._membership_renew_former_member(
            self.date_from, self.env.context.get("renew"))

    @api.model
    @job(default_channel="root.membership_renew_former_member")
    def _membership_renew_former_member(self, date_from, renew):
        if renew:
            self.env["membership.line"]._launch_renew(date_from=date_from)
        else:
            self.env["membership.line"]._launch_former_member(
                date_from=date_from)
