# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    distribution_list_id = fields.Many2one(
        "distribution.list",
        "Distribution List",
        ondelete="cascade",
    )

    @api.model
    def create(self, vals):
        """
        This override allows the user to force the mass mail to
        the distribution list even if the header check-box was checked
        :param vals: dict
        :return: self recordset
        """
        context = self.env.context.copy()
        if "distribution_list_id" in vals and "active_domain" in context:
            context.pop("active_domain")
            if vals.get("use_active_domain"):
                vals.update(
                    {
                        "use_active_domain": False,
                        "composition_mode": "mass_mail",
                    }
                )

        return super(MailComposeMessage, self.with_context(context)).create(vals)

    def send_mail(self, auto_commit=False):
        """
        With a distribution list, we compute active_ids here,
        except if we are in an automation process.
        """
        distribution_list = self.distribution_list_id
        if distribution_list:
            self = self.with_context(active_model="res.partner")
        if distribution_list and (
            not self.mass_mailing_id
            or (self.mass_mailing_id and not self.mass_mailing_id.automation)
        ):
            target_ids = distribution_list._get_target_from_distribution_list()
            if target_ids._name != "res.partner":
                target_ids = target_ids.mapped("partner_id")
            mailing_domain = [("id", "in", target_ids.ids)]
            active_ids = self.env["res.partner"].search(mailing_domain)
            self = self.with_context(active_ids=active_ids.ids)
            self.model = "res.partner"  # we do not want to have virtual.target here
        return super().send_mail(auto_commit=auto_commit)
