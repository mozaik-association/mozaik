# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    # Fake field for auto-completing placeholder
    placeholder_id = fields.Many2one(
        comodel_name="email.template.placeholder",
        string="Placeholder",
        domain=[("model_id", "=", "res.partner")],
    )
    placeholder_value = fields.Char(
        help="Copy this text to the email body. It'll be replaced by the "
        "value from the document",
    )

    @api.onchange("placeholder_id")
    def _onchange_placeholder_id(self):
        for mailing in self:
            if mailing.placeholder_id:
                placeholder_value = mailing.placeholder_id.placeholder
                mailing.placeholder_id = False
                mailing.placeholder_value = placeholder_value
