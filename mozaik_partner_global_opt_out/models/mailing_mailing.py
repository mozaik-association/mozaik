# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    include_opt_out_contacts = fields.Boolean(
        default=False,
        string="Include opt-out contacts",
        help="If True, include contacts whose email is blacklisted.",
    )

    def _process_mass_mailing_queue(self):
        """
        Put in context all mailings for which we need to include
        opt-out contacts (even if they don't have to be sent now)
        """
        mailings_with_include_opt_out = self.env["mailing.mailing"].search(
            [("include_opt_out_contacts", "=", True)]
        )
        super(
            MailingMailing,
            self.with_context(
                {"include_opt_out_contacts_mailings": mailings_with_include_opt_out.ids}
            ),
        )._process_mass_mailing_queue()
