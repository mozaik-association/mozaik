# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    is_counter_registration = fields.Boolean(
        string="Counter Registration",
        help="Registration at the counter after the start of the event,"
        "doesn't trigger the 'after_sub' communications.",
    )

    def default_get(self, fields_list):
        """
        We want this logic to apply only from the view, hence the use of 'default_get()'.
        """
        vals = super().default_get(fields_list)
        if "event_id" in vals:
            event = self.env["event.event"].browse(vals["event_id"]).exists()
            if event and event.date_begin < fields.Datetime.now():
                vals["is_counter_registration"] = True
        return vals

    def action_confirm(self):
        """
        Counter registration should by-pass the confirmation state
        and its associated communications.
        We manually create 'event.mail.registration' records in order to avoid "after-sub"
        communications to be sent anytime.
        """
        counter_registrations = self.browse()
        for rec in self.filtered("is_counter_registration"):
            for mail_scheduler in rec.event_id.event_mail_ids.filtered(
                lambda scheduler: scheduler.interval_type == "after_sub"
            ):
                self.env["event.mail.registration"].create(
                    {
                        "scheduler_id": mail_scheduler.id,
                        "registration_id": rec.id,
                        "mail_sent": True,
                    }
                )
            rec.action_set_done()
            counter_registrations |= rec
        super(EventRegistration, self - counter_registrations).action_confirm()
