# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    multi_send_same_email = fields.Boolean(
        string="Multi sending to same email",
        help="The email can be sent several times to the same email address, "
        "if it appears several times into the recipients list.",
    )

    @api.onchange("mailing_model_id")
    def onchange_multi_send_same_email(self):
        """
        multi_send_same_email cannot be used if mailing_model_id is not
        distribution.list or res.partner
        """
        self.ensure_one()
        if not self.mailing_model_id or self.mailing_model_id.model not in [
            "res.partner",
            "distribution.list",
        ]:
            self.multi_send_same_email = False

    @api.constrains("mailing_model_id", "multi_send_same_email")
    def _check_distribution_list_ids(self):
        """
        multi_send_same_email cannot be used if mailing_model_id is not
        distribution.list or res.partner
        """
        for record in self:
            if (
                record.multi_send_same_email
                and record.mailing_model_id
                and record.mailing_model_id.model
                not in ["res.partner", "distribution.list"]
            ):
                raise ValidationError(
                    _(
                        "'Multi sending to same email' cannot be True "
                        "if mailing model is different from 'Contact' or 'Distribution List'."
                    )
                )
