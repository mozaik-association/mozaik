# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import random
import threading
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools
from odoo.tools import exception_to_unicode

_logger = logging.getLogger(__name__)

_INTERVALS = {
    "days": lambda interval: relativedelta(days=interval),
    "weeks": lambda interval: relativedelta(days=7 * interval),
    "months": lambda interval: relativedelta(months=interval),
    "now": lambda interval: relativedelta(hours=0),
}


class PetitionMail(models.Model):
    _name = "petition.mail"
    _rec_name = "petition_id"
    _description = "Petition Automated Mailing"

    petition_id = fields.Many2one(
        "petition.petition", string="Petition", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(string="Display Order")
    notification_type = fields.Selection(
        selection=[("mail", "Mail")], string="Send", default="mail", required=True
    )
    interval_nbr = fields.Integer("Interval", default=1)
    interval_unit = fields.Selection(
        [
            ("now", "Immediately"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Unit",
        default="days",
        required=True,
    )
    interval_type = fields.Selection(
        [
            ("after_sub", "After each signature"),
            ("before_petition", "Before the petition"),
            ("after_petition", "After the petition"),
        ],
        string="Trigger ",
        default="before_petition",
        required=True,
    )
    template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
        domain=[("model", "=", "petition.registration")],
        ondelete="restrict",
        help="This field contains the template of the mail "
        "that will be automatically sent",
    )
    scheduled_date = fields.Date(
        "Scheduled Sent Mail", compute="_compute_scheduled_date", store=True
    )
    mail_registration_ids = fields.One2many(
        "petition.mail.registration", "scheduler_id"
    )
    mail_sent = fields.Boolean("Mail Sent on Petition", copy=False)
    done = fields.Boolean(string="Sent", compute="_compute_done", store=True)

    @api.depends(
        "mail_sent",
        "interval_type",
        "petition_id.registration_ids",
        "mail_registration_ids.mail_sent",
    )
    def _compute_done(self):
        for mail in self:
            if mail.interval_type in ["before_petition", "after_petition"]:
                mail.done = mail.mail_sent
            else:
                mail.done = len(mail.mail_registration_ids) == len(
                    mail.petition_id.registration_ids
                ) and all(mail.mail_sent for mail in mail.mail_registration_ids)

    @api.depends(
        "petition_id.date_begin",
        "petition_id.date_end",
        "interval_type",
        "interval_unit",
        "interval_nbr",
    )
    def _compute_scheduled_date(self):
        for mail in self:
            if mail.interval_type == "after_sub":
                d, sign = mail.petition_id.create_date.date(), 1
            elif mail.interval_type == "before_petition":
                d, sign = mail.petition_id.date_begin, -1
            else:
                d, sign = mail.petition_id.date_end, 1

            mail.scheduled_date = (
                d + _INTERVALS[mail.interval_unit](sign * mail.interval_nbr)
                if d
                else False
            )

    def execute(self):
        for mail in self:
            today = fields.Date.today()
            if mail.interval_type == "after_sub":
                # update registration lines
                lines = [
                    (0, 0, {"registration_id": registration.id})
                    for registration in (
                        mail.petition_id.registration_ids
                        - mail.mapped("mail_registration_ids.registration_id")
                    )
                ]
                if lines:
                    mail.write({"mail_registration_ids": lines})
                # execute scheduler on registrations
                mail.mail_registration_ids.execute()
            else:
                # Do not send emails if the mailing was scheduled
                # before the petition but the petition is over
                if (
                    not mail.mail_sent
                    and mail.scheduled_date <= today
                    and mail.notification_type == "mail"
                    and (
                        mail.interval_type != "before_petition"
                        or mail.petition_id.date_end > today
                    )
                ):
                    mail.petition_id.send_mail_to_signatories(mail.template_id.id)
                    mail.write({"mail_sent": True})
        return True

    @api.model
    def _warn_template_error(self, scheduler, exception):
        # We warn ~ once by hour ~ instead of every 10 min
        # if the interval unit is more than 'hours'.
        if random.random() < 0.1666 or scheduler.interval_unit == "now":
            ex_s = exception_to_unicode(exception)
            try:
                petition, template = scheduler.petition_id, scheduler.template_id
                emails = list(
                    {
                        petition.organizer_id.email,
                        petition.user_id.email,
                        template.write_uid.email,
                    }
                )
                subject = _(
                    "WARNING: Petition Scheduler Error for petition: %s", petition.name
                )
                body = _(
                    """Petition Scheduler for:
      - Petition: %(petition_name)s (%(petition_id)s)
      - Scheduled: %(date)s
      - Template: %(template_name)s (%(template_id)s)

    Failed with error:
      - %(error)s

    You receive this email because you are:
      - the organizer of the petition,
      - or the responsible of the petition,
      - or the last writer of the template.
    """,
                    petition_name=petition.name,
                    petition_id=petition.id,
                    date=scheduler.scheduled_date,
                    template_name=template.name,
                    template_id=template.id,
                    error=ex_s,
                )
                email = self.env["ir.mail_server"].build_email(
                    email_from=self.env.user.email,
                    email_to=emails,
                    subject=subject,
                    body=body,
                )
                self.env["ir.mail_server"].send_email(email)
            except Exception as e:  # pylint: disable=W0703
                _logger.error(
                    "Exception while sending traceback "
                    "by email: %s.\n Original Traceback:\n%s",
                    e,
                    exception,
                )

    @api.model
    def run(self, autocommit=False):
        schedulers = self.search(
            [
                ("done", "=", False),
                (
                    "scheduled_date",
                    "<=",
                    date.strftime(
                        fields.date.today(), tools.DEFAULT_SERVER_DATE_FORMAT
                    ),
                ),
            ]
        )
        for scheduler in schedulers:
            try:
                with self.env.cr.savepoint():
                    # Prevent a mega prefetch of the registration ids
                    # of all the petitions of all the schedulers
                    self.browse(scheduler.id).execute()
            except Exception as e:  # pylint: disable=W0703
                _logger.exception(e)
                self.invalidate_cache()
                self._warn_template_error(scheduler, e)
            else:
                if autocommit and not getattr(
                    threading.currentThread(), "testing", False
                ):
                    self.env.cr.commit()  # pylint: disable=E8102
        return True


class PetitionMailRegistration(models.Model):
    _name = "petition.mail.registration"
    _description = "Registration Mail Scheduler"
    _rec_name = "scheduler_id"
    _order = "scheduled_date DESC"

    scheduler_id = fields.Many2one(
        "petition.mail", "Mail Scheduler", required=True, ondelete="cascade"
    )
    registration_id = fields.Many2one(
        "petition.registration", "Signatory", required=True, ondelete="cascade"
    )
    scheduled_date = fields.Date(
        "Scheduled Time", compute="_compute_scheduled_date", store=True
    )
    mail_sent = fields.Boolean("Mail Sent")

    @api.depends(
        "registration_id.date_open",
        "scheduler_id.interval_unit",
        "scheduler_id.interval_type",
    )
    def _compute_scheduled_date(self):
        for mail in self:
            if mail.registration_id:
                date_open = mail.registration_id.date_open
                date_open_date = date_open or fields.Date.today()
                mail.scheduled_date = date_open_date + _INTERVALS[
                    mail.scheduler_id.interval_unit
                ](mail.scheduler_id.interval_nbr)
            else:
                mail.scheduled_date = False

    def execute(self):
        today = fields.Date.today()
        todo = self.filtered(
            lambda reg_mail: not reg_mail.mail_sent
            and (reg_mail.scheduled_date and reg_mail.scheduled_date <= today)
            and reg_mail.scheduler_id.notification_type == "mail"
        )
        for reg_mail in todo:
            reg_mail.scheduler_id.template_id.send_mail(reg_mail.registration_id.id)
            reg_mail.write({"mail_sent": True})
