# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    global_opt_out = fields.Boolean(
        string="Global opt-out",
        help="If true, the email address is blacklisted",
        compute="_compute_global_opt_out",
        store=True,
        inverse="_inverse_global_opt_out",
        tracking=True,
    )

    def write(self, vals):
        if not vals.get("email", True):
            # Forced to call write (instead of update vals) to trigger inverse method
            self.write({"global_opt_out": False})
        return super().write(vals)

    @api.depends("email")
    def _compute_global_opt_out(self):
        for record in self:
            record.global_opt_out = False
            mb = self.env["mail.blacklist"].search([("email", "=", record.email)])
            if mb:
                record.global_opt_out = mb.active

    def _inverse_global_opt_out(self):
        skip = self._context.get("skip_mail_blacklist_update", False)
        if not skip:
            for record in self:
                if record.global_opt_out:
                    if record.email:
                        self.env["mail.blacklist"]._add(record.email)
                else:
                    mb = self.env["mail.blacklist"].search(
                        [("email", "=", record.email)]
                    )
                    if mb:
                        self.env["mail.blacklist"].action_remove_with_reason(
                            record.email, "Global opt out set to False."
                        )
