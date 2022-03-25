# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    multi_send_same_email = fields.Boolean(
        string="Multi sending to same email",
        help="The email can be sent several times to the same email address, "
        "if it appears several times into the recipients list.",
    )

    @api.model
    def create(self, vals):
        """
        We check if the mailing_mailing has multi_send_same_email
        """
        res = super().create(vals)
        mass_mailing_id = res.mass_mailing_id
        if len(mass_mailing_id) == 1 and mass_mailing_id.multi_send_same_email:
            res.write({"multi_send_same_email": True})
        return res

    def _already_seen(self, seen_list, mail_to):
        """
        If multi_send_same_email is True, we always return False.
        """
        res = super()._already_seen(seen_list, mail_to)
        if self.multi_send_same_email:
            return False
        return res
