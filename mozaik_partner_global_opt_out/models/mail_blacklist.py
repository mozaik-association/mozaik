# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailBlacklist(models.Model):

    _inherit = "mail.blacklist"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._update_global_opt_our_on_partners()
        return res

    def write(self, vals):
        super().write(vals)
        self._update_global_opt_our_on_partners()

    def unlink(self):
        # Archive records to update global_opt_out on partners before unlink.
        self.write({"active": False})
        super().unlink()

    def _update_global_opt_our_on_partners(self):
        # Looking for all partners with wrong global_opt_out to update it.
        for mail_blacklist in self:
            partners = self.env["res.partner"].search(
                [
                    "&",
                    ("email", "=", mail_blacklist.email),
                    "!",
                    ("global_opt_out", "=", mail_blacklist.active),
                ]
            )
            if partners:
                partners.with_context({"skip_mail_blacklist_update": True}).write(
                    {"global_opt_out": mail_blacklist.active}
                )
