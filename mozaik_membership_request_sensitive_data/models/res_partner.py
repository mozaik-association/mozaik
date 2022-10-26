# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _schedule_activity(self, note, days):
        """
        Schedule an activity on self.
        """
        self.ensure_one()
        vals = {
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": _("Sensitive data to modify on partner"),
            "note": note,
            "date_deadline": datetime.datetime.today() + datetime.timedelta(days=days),
            "automated": True,
            "res_model_id": self.env["ir.model"]
            .search([("model", "=", "res.partner")])
            .id,
            "res_id": self.id,
        }
        control_user_id = int(
            self.sudo()
            .env["ir.config_parameter"]
            .get_param("force_autoval_control_user")
        )
        if control_user_id:
            user_id = self.env["res.users"].search([("id", "=", control_user_id)])
        else:
            user_id = self.env.ref("base.user_admin")
        if user_id:
            vals["user_id"] = user_id.id
        self["activity_ids"] = [(0, 0, vals)]
