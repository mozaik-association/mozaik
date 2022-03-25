# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    include_opt_out_contacts = fields.Boolean(
        default=False,
        string="Include opt-out contacts",
        help="If True, include contacts whose email is blacklisted.",
    )

    @api.model
    def create(self, vals):
        """
        If coming from _process_mass_mailing_queue,
        we check if the mailing_mailing has include_opt_out_contacts
        """
        res = super().create(vals)
        mass_mailing_id = res.mass_mailing_id
        if len(mass_mailing_id) == 1 and mass_mailing_id.id in self._context.get(
            "include_opt_out_contacts_mailings", []
        ):
            res.write({"include_opt_out_contacts": True})
        return res

    def _to_cancel_opt_out(
        self, opt_out_list, mail_to, mail_values, res_id, blacklisted_emails
    ):
        res = super()._to_cancel_opt_out(
            opt_out_list, mail_to, mail_values, res_id, blacklisted_emails
        )
        if (
            self.include_opt_out_contacts
            and mail_values.get("state", False) == "cancel"
            and mail_values["model"] == "res.partner"
            and self.env["res.partner"].browse(mail_values["res_id"]).global_opt_out
        ):
            return False
        return res
