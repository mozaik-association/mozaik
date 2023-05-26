# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IntAssembly(models.Model):

    _inherit = "int.assembly"

    def _get_summary_recipients(self):
        """
        Build recipients list of the summary mail
        regarding summary_mails_recipient field of internal mandate categories
        """
        self.ensure_one()
        mandates = self.env["int.mandate"].search(
            [
                ("int_assembly_id", "=", self.id),
                ("mandate_category_id.summary_mails_recipient", "=", True),
            ]
        )
        recipients = mandates.mapped("partner_id")
        return recipients

    def send_last_changes(self):
        """
        Send the summary mails to internal assemblies
        """
        ctx = dict(self.env.context, active_ids=False)
        composer = self.env["mail.compose.message"]
        template_id = self.env.ref(
            "mozaik_membership_last_changes_report.reference_data_changes_email_template"
        )
        for assembly in self:
            partners = assembly._get_summary_recipients()
            if not partners:
                continue
            ctx["active_id"] = assembly.id
            # lang must be set here to render correctly the state name
            # of members in the html body
            ctx["lang"] = assembly.partner_id.lang
            vals = {
                "model": self._name,
                "composition_mode": "mass_mail",
                "template_id": template_id.id,
                "partner_ids": [(6, 0, partners.ids)],
                "notify": True,
            }
            new_composer = composer.with_context(ctx).create(vals)
            values = new_composer.onchange_template_id(
                template_id.id, "mass_mail", self._name, False
            )["value"]
            if values.get("attachment_ids"):
                values["attachment_ids"] = [(6, 0, values["attachment_ids"])]
            new_composer.write(values)
            new_composer.send_mail()
