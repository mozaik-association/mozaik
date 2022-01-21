# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    include_opt_out_contacts = fields.Boolean(
        default=False,
        string="Include opt-out contacts",
        help="If True, include contacts whose email is blacklisted.",
    )

    def get_mail_values(self, res_ids):
        """
        If the wizard's model is `email.coordinate` then the recipient is the
        email of the `email.coordinate`
        """
        res = super().get_mail_values(res_ids)
        if self.include_opt_out_contacts:
            for key in res.keys():
                item = res[key]
                if (
                    "state" in item
                    and item["state"] == "cancel"
                    and item["model"] == "res.partner"
                    and self.env["res.partner"].browse(item["res_id"]).global_opt_out
                ):
                    item.pop("state")
        return res
