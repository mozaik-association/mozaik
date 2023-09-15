# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MozaikMassMailingSendingControl(models.TransientModel):

    _name = "mozaik.mass.mailing.sending.control"
    _description = "Mozaik Mass Mailing Sending Control"

    mailing_id = fields.Many2one("mailing.mailing", required=True)
    number_recipients = fields.Integer(readonly=True)
    number_control = fields.Integer()

    def doit(self):
        self.ensure_one()
        if self.number_recipients != self.number_control:
            raise ValidationError(_("Please enter the correct number of recipients"))
        if self.env.context.get("sending_operation") == "put_in_queue":
            return self.mailing_id.action_put_in_queue()
        if self.env.context.get("sending_operation") == "schedule":
            return self.mailing_id.action_schedule()
