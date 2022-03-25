# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    def _get_blacklisted_ids(self, res_ids):
        """
        Copy part of the get_mail_values method in
        odoo/addons/mail/wizards/mail_compose_message.py (see lines 286 to 295).
        Note that since v15, this code was cut in the same way as here
        (see method _get_blacklist_record_ids line 512)

        Returns a subset of res_ids, where the corresponding emails are blacklisted.
        """
        blacklisted_rec_ids = set()
        if self.composition_mode == "mass_mail" and issubclass(
            type(self.env[self.model]), self.pool["mail.thread.blacklist"]
        ):
            self.env["mail.blacklist"].flush(["email"])
            self._cr.execute("SELECT email FROM mail_blacklist WHERE active=true")
            blacklist = {x[0] for x in self._cr.fetchall()}
            if blacklist:
                targets = (
                    self.env[self.model].browse(res_ids).read(["email_normalized"])
                )
                # First extract email from recipient before comparing with blacklist
                blacklisted_rec_ids.update(
                    target["id"]
                    for target in targets
                    if target["email_normalized"] in blacklist
                )
        return blacklisted_rec_ids

    def _get_partner_emails(self, res_ids, res):
        """
        Copy part of the get_mail_values method in
        odoo/addons/mass_mailing/wizards/mail_compose_message.py
        (see lines 46 to 55)
        """
        recipient_partners_ids = []
        for res_id in res_ids:
            mail_values = res[res_id]
            if mail_values.get("recipient_ids"):
                # recipient_ids is a list of x2m command tuples at this point
                recipient_partners_ids.append(mail_values.get("recipient_ids")[0][1])
        read_partners = self.env["res.partner"].browse(recipient_partners_ids)

        return {p.id: p.email for p in read_partners}

    def _to_cancel_opt_out(
        self, opt_out_list, mail_to, mail_values, res_id, blacklisted_emails
    ):
        """
        Copy first part of the if condition in
        odoo/addons/mass_mailing/wizards/mail_compose_message.py#L67

        Intended to be extended if we want to include opt-out contacts
        """
        return (opt_out_list and mail_to in opt_out_list) or (
            res_id in blacklisted_emails
        )

    def _already_seen(self, seen_list, mail_to):
        """
        Copy second part of the if condition in
        odoo/addons/mass_mailing/wizards/mail_compose_message.py#L67

        Intended to be extended if we want to send several emails to the
        same email address.
        """
        return seen_list and mail_to in seen_list

    def get_mail_values(self, res_ids):
        """
        Re-write part of the get_mail_values method in
        odoo/addons/mass_mailing/wizards/mail_compose_message.py
        (see lines 57 to 72).

        Make changes due to (un)canceling an email:
        - if mail was canceled and is not canceled anymore: change state
        and remove 'ignored' datetime.
        - if mail wasn't canceled but is now canceled: change state and
        add 'ignored' datetime.
        """
        res = super().get_mail_values(res_ids)

        if (
            self.composition_mode == "mass_mail"
            and (self.mass_mailing_name or self.mass_mailing_id)
            and self.env["ir.model"]
            .sudo()
            .search(
                [("model", "=", self.model), ("is_mail_thread", "=", True)], limit=1
            )
        ):
            partners_email = self._get_partner_emails(res_ids, res)

            opt_out_list = self._context.get("mass_mailing_opt_out_list")
            blacklisted_emails = self._get_blacklisted_ids(res_ids)
            # Need to re-compute the seen list without taking into account
            # the actual mail_values.
            seen_list = (
                self.mass_mailing_id._get_seen_list() if self.mass_mailing_id else None
            )
            for res_id in res_ids:
                mail_values = res[res_id]
                is_canceled_mail = False
                if mail_values.get("email_to"):
                    mail_to = tools.email_normalize(mail_values["email_to"])
                else:
                    partner_id = (mail_values.get("recipient_ids") or [(False, "")])[0][
                        1
                    ]
                    mail_to = tools.email_normalize(partners_email.get(partner_id))

                if self._to_cancel_opt_out(
                    opt_out_list, mail_to, mail_values, res_id, blacklisted_emails
                ) or self._already_seen(seen_list, mail_to):
                    is_canceled_mail = True
                elif seen_list is not None:
                    seen_list.add(mail_to)

                if mail_values.get("state", False) != "cancel" and is_canceled_mail:
                    # Mail was not cancelled but we want to cancel now
                    mail_values["state"] = "cancel"
                    mail_values["mailing_trace_ids"][-1][2].update(
                        {"ignored": fields.Datetime.now()}
                    )

                elif (
                    mail_values.get("state", False) == "cancel" and not is_canceled_mail
                ):
                    # Mail was cancelled but we want to send it.
                    mail_values.pop("state")
                    if mail_values["mailing_trace_ids"]:
                        last_mailing_trace = mail_values["mailing_trace_ids"][-1]
                        last_mailing_trace[2].pop("ignored")

        return res
