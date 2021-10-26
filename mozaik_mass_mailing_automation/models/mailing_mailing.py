# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MassMailing(models.Model):

    _inherit = "mailing.mailing"

    automation = fields.Boolean(string="Automation", default=False)
    next_execution = fields.Datetime(
        string="Next Execution of the Automation Process",
        help="Date and time of the next execution. "
        "New sendings will be planned every 24 hours.",
    )
    schedule_date = fields.Datetime(
        compute="_compute_schedule_date",
        store=True,
    )

    @api.constrains("automation", "next_execution")
    def _check_next_execution(self):
        for rec in self:
            if rec.automation and not rec.next_execution:
                raise ValidationError(
                    _(
                        "Since automation is set to True, "
                        "you have to fill the 'Next Execution' field."
                    )
                )

    @api.depends("automation", "next_execution")
    def _compute_schedule_date(self):
        for record in self:
            if record.automation:
                record.schedule_date = record.next_execution
            elif record.next_execution:
                # if record.next_execution, it means that record.automation
                # was True at some point
                record.schedule_date = False
            else:
                record.schedule_date = record.schedule_date

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
        for mailing in mass_mailings.filtered(lambda l: l.automation):
            next_execution = fields.Datetime.now() + relativedelta(days=1)
            next_execution = next_execution.replace(
                hour=mailing.next_execution.hour,
                minute=mailing.next_execution.minute,
                second=mailing.next_execution.second,
            )
            mailing.write({"next_execution": next_execution})
        return 0
