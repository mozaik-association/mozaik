# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    def _check_control_needed(self):
        self.ensure_one()
        if not (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mass_mailing.sending_control")
        ):
            return (False, 0)
        recipient_number = len(self._get_recipients())
        sending_control_number = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mass_mailing.sending_control_number")
        )
        return (
            sending_control_number > 0 and recipient_number >= sending_control_number,
            recipient_number,
        )

    def action_put_in_queue_with_control(self):
        self.ensure_one()
        control_needed, recipient_number = self._check_control_needed()
        if control_needed:
            return {
                "type": "ir.actions.act_window",
                "name": "Sending Control",
                "res_model": "mozaik.mass.mailing.sending.control",
                "context": {
                    "default_mailing_id": self.id,
                    "sending_operation": "put_in_queue",
                    "default_number_recipients": recipient_number,
                },
                "target": "new",
                "view_mode": "form",
            }

        return self.action_put_in_queue()

    def action_schedule_with_control(self):
        self.ensure_one()
        control_needed, recipient_number = self._check_control_needed()
        if control_needed:
            return {
                "type": "ir.actions.act_window",
                "name": "Sending Control",
                "res_model": "mozaik.mass.mailing.sending.control",
                "context": {
                    "default_mailing_id": self.id,
                    "sending_operation": "schedule",
                    "default_number_recipients": recipient_number,
                },
                "target": "new",
                "view_mode": "form",
            }

        return self.action_schedule()
