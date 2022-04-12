# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


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
