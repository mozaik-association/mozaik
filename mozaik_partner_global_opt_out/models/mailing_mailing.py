# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    include_opt_out_contacts = fields.Boolean(
        default=False,
        string="Include opt-out contacts",
        help="If True, include contacts whose email is blacklisted.",
    )

    @api.onchange("mailing_model_id")
    def onchange_include_opt_out_contacts(self):
        """
        include_opt_out_contacts cannot be used if mailing_model_id is not
        distribution.list or res.partner
        """
        self.ensure_one()
        if not self.mailing_model_id or self.mailing_model_id.model not in [
            "res.partner",
            "distribution.list",
        ]:
            self.include_opt_out_contacts = False

    @api.constrains("mailing_model_id", "include_opt_out_contacts")
    def _check_include_opt_out_contacts(self):
        """
        include_opt_out_contacts cannot be used if mailing_model_id is not
        distribution.list or res.partner
        """
        for record in self:
            if (
                record.include_opt_out_contacts
                and record.mailing_model_id
                and record.mailing_model_id.model
                not in ["res.partner", "distribution.list"]
            ):
                raise ValidationError(
                    _(
                        "'Include opt-out contacts' cannot be True "
                        "if mailing model is different from 'Contact' or 'Distribution List'."
                    )
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
