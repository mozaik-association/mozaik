# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class MassMailing(models.Model):

    _inherit = "mailing.mailing"

    automation = fields.Boolean(string="Automation", default=False)
    next_execution = fields.Datetime(
        string="Next Execution of the Automation Process",
        default=datetime.now(),
        help="Date and time of the next execution. "
        "New sendings will be planned every 24 hours.",
    )
    schedule_date = fields.Datetime(
        string="Scheduled for",
        tracking=True,
        compute="_compute_schedule_date",
        store=True,
    )  # becomes a compute in case of automation

    @api.depends("automation", "next_execution")
    def _compute_schedule_date(self):
        for record in self:
            if record.automation:
                record.schedule_date = record.next_execution
            elif record.next_execution > datetime.now():
                record.schedule_date = False

    def _process_mass_mailing_queue(self):
        mass_mailings = self.search(
            [
                ("automation", "=", True),
                (
                    "state",
                    "in",
                    ("in_queue", "sending", "done"),
                ),  # in_queue is necessary to consider these mailings in for loop
                ("schedule_date", "<", datetime.now()),
            ]
        )
        mass_mailings.write({"state": "in_queue"})
        super()._process_mass_mailing_queue()
        for mailing in mass_mailings:
            mailing.write(
                {"next_execution": mailing.next_execution + relativedelta(days=1)}
            )
        return 0
