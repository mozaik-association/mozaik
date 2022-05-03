# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

CONFIRMATION_MSGS = [
    ("not_found", "Registration not found."),
    (
        "draft",
        "Registration wasn't confirmed. Do you want to validate the attendance?",
    ),
    ("open", "Participant successfully attended."),
    ("done", "Error: this participant already attended."),
    ("cancel", "Error: registration was canceled."),
]


class BarcodeScanner(models.TransientModel):

    _name = "barcode.scanner"
    _description = "Barcode Scanner Wizard"

    barcode = fields.Char()
    event_id = fields.Many2one("event.event", string="Associated Event")
    event_registration_id = fields.Many2one("event.registration")
    confirmation_msg = fields.Selection(
        selection=CONFIRMATION_MSGS, string="Information"
    )
    lastname = fields.Char(
        string="Attendee's lastname",
        related="event_registration_id.lastname",
        store=True,
    )
    firstname = fields.Char(
        string="Attendee's firstname",
        related="event_registration_id.lastname",
        store=True,
    )

    @api.onchange("barcode")
    def _onchange_barcode(self):
        self.ensure_one()
        if self.event_id:
            self.event_registration_id = self.env["event.registration"].search(
                [("barcode", "=", self.barcode), ("event_id", "=", self.event_id.id)]
            )
        if self.event_registration_id:
            self._process_event_registration_actions()
        elif self.barcode:
            self.confirmation_msg = "not_found"

    def _manage_registration(self, registration):
        """
        :reg: event.registration record
        If state == 'done' -> Error message since the person already attended
        If state == 'cancel' -> Error message since the registration is canceled
        If state == 'draft' -> Ask if we want to validate the attendance even
          if registration is not confirmed
        If state == 'open' -> Set the registration as 'done'
        """
        state = registration.state
        self.confirmation_msg = state
        if state == "open":
            registration["state"] = "done"

    def _process_event_registration_actions(self):
        registration = self.event_registration_id
        if not registration:
            return
        self._manage_registration(registration)

    def open_next_scan(self):
        action = self.event_id.open_barcode_scanner()
        action["context"] = {"default_event_id": self.event_id.id}
        return action

    def confirm_open_next_scan(self):
        self.event_registration_id.ensure_one()
        self.event_registration_id["state"] = "done"
        return self.open_next_scan()
