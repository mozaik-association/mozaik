# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
            if record.next_departure < fields.Datetime.now():
                record.next_departure_msg = (
                    "Other mailings are currently being sent. "
                    "This mailing will be sent as soon as possible"
                )
            else:
                record.next_departure_msg = (
                    "This mailing is scheduled for "
                    "%(next_departure)s" % {"next_departure": record.next_departure}
                )
