# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    next_departure_msg = fields.Char(compute="_compute_next_departure_msg")

    def _compute_next_departure_msg(self):
        """
        If next departure is in the future -> keep the actual message.
        If next departure is in the past -> don't show the schedule date.
        """
        for record in self:
            if record.next_departure + relativedelta(minutes=1) < fields.Datetime.now():
                record.next_departure_msg = (
                    "Other mailings are currently being sent. "
                    "This mailing will be sent as soon as possible."
                )
            else:
                next_departure_utc = pytz.utc.localize(record.next_departure)
                next_departure_now = next_departure_utc.astimezone(
                    pytz.timezone(self._context.get("tz") or "UTC")
                )
                next_departure_now = next_departure_now.strftime("%d/%m/%Y %H:%M:%S")
                record.next_departure_msg = (
                    "This mailing is scheduled for "
                    "%(next_departure)s" % {"next_departure": next_departure_now}
                )
