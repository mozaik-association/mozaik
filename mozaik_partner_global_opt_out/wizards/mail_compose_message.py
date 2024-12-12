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

    @api.model
    def _is_mail_canceled_because_of_opt_out(self, mail_values, res_id):
        """
        Odoo can cancel a mail for a lot of reasons. One of them is
        because the email is blacklisted.
        When we want to include opt-out contacts, we want to uncancel
        emails (and ONLY the ones) that were canceled because
        of a global opt-out on the partner.
        There are different ways of performing this check, depending
        on the mailing model.
        This method deals with the different ways.
        """
        if mail_values["model"] == "res.partner":
            return self.env["res.partner"].browse(mail_values["res_id"]).global_opt_out
        if mail_values["model"] == "mailing.contact":
            # Several partners can share the same email. If one of the partners
            # has global opt out, we consider that the email itself has the global opt-out.
            return any(
                self.env["res.partner"]
                .search([("email", "=", mail_values["email_to"])])
                .mapped("global_opt_out")
            )

    def _to_cancel_opt_out(
        self, opt_out_list, mail_to, mail_values, res_id, blacklisted_emails
    ):
        """
        This method returns the res_id of mails we REALLY want to cancel
        (because email is blacklisted for eg).
        If include_opt_out_contacts is set, we want to force the sending
        of the email, hence uncancel these emails, hence we return False.
        """
        res = super()._to_cancel_opt_out(
            opt_out_list, mail_to, mail_values, res_id, blacklisted_emails
        )
        if (
            self.include_opt_out_contacts
            and mail_values.get("state", False) == "cancel"
            and self._is_mail_canceled_because_of_opt_out(mail_values, res_id)
        ):
            return False
        return res
