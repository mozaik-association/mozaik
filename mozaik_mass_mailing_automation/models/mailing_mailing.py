# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_INTERVALS = {
    "hours": lambda interval: relativedelta(hours=interval),
    "days": lambda interval: relativedelta(days=interval),
    "weeks": lambda interval: relativedelta(days=7 * interval),
    "months": lambda interval: relativedelta(months=interval),
    "years": lambda interval: relativedelta(years=interval),
}


class MassMailing(models.Model):

    _inherit = "mailing.mailing"

    automation = fields.Boolean(string="Automation", default=False)
    next_execution = fields.Datetime(
        string="Next Execution",
        help="Date and time of the next execution of the automation process.",
    )
    time_interval_nbr = fields.Integer(
        "Time Interval",
        default=1,
        help="Time interval between two consecutive sendings.",
    )
    time_interval_unit = fields.Selection(
        [
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        string="Unit",
        default="days",
    )

    schedule_date = fields.Datetime(
        compute="_compute_schedule_date",
        store=True,
    )

    _sql_constraints = [
        (
            "time_interval_nbr_positive",
            "CHECK (time_interval_nbr > 0)",
            "Time interval has to be positive.",
        )
    ]

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

    @api.constrains("automation", "mailing_model_id")
    def _check_automation(self):
        """
        Automation cannot work if mailing model is neither distribution.list
        not mailing.list
        """
        for rec in self:
            if (
                rec.automation
                and rec.mailing_model_id
                and rec.mailing_model_id.model
                not in ["mailing.list", "distribution.list"]
            ):
                raise ValidationError(
                    _(
                        "Automation is only allowed for distribution lists and mailing lists."
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

    def _add_time_interval(self, current_date, mailing):
        return current_date + _INTERVALS[mailing.time_interval_unit](
            mailing.time_interval_nbr
        )

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

        # We need to recompute the mailing domains, if new partners are concerned
        # by the target list (distribution list, of mailing list, or...)
        mass_mailings._compute_mailing_domain()

        super()._process_mass_mailing_queue()
        for mailing in mass_mailings.filtered("automation"):
            next_execution = fields.Datetime.now()
            next_execution = next_execution.replace(
                hour=mailing.next_execution.hour,
                minute=mailing.next_execution.minute,
                second=mailing.next_execution.second,
            )
            next_execution = self._add_time_interval(next_execution, mailing)
            mailing.write({"next_execution": next_execution})
        return 0
