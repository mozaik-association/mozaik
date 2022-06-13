# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
    )
    use_custom_templates = fields.Boolean(default=False, string="Use mail templates")
    body_arch_custom = fields.Html(string="Body (mail template)", translate=False)

    @api.model
    def create(self, vals):
        mass_mailing_from_mass_action = self._context.get(
            "mass_mailing_from_mass_action", False
        )
        vals_to_add = {}
        use_custom_templates = vals.get("use_custom_templates", False)
        if (
            mass_mailing_from_mass_action
            and "body_html" in vals
            and "body_arch" not in vals
        ):
            vals_to_add["body_arch"] = vals["body_html"]
        elif use_custom_templates and "body_arch_custom" in vals:
            vals_to_add["body_html"] = vals["body_arch_custom"]
            vals_to_add["body_arch"] = vals["body_arch_custom"]

        if vals_to_add.keys():
            vals.update(vals_to_add)
        return super().create(vals)

    def write(self, vals):
        """
        When modifying body_arch_custom, we must be careful: use_custom_templates
        has to be True for all records to take care of the modifications.
        """
        if "body_arch_custom" in vals:
            actual_use_custom_templates = self.mapped("use_custom_templates")
            if (
                "use_custom_templates" not in vals
                and len(actual_use_custom_templates) > 1
            ):
                raise ValidationError(
                    _(
                        "You are trying to modify body_arch_custom on several mass_mailings"
                        "at the same time, but use_custom_templates does not have "
                        "the same value on all mass mailings."
                    )
                )
            use_custom_templates = (
                vals["use_custom_templates"]
                if "use_custom_templates" in vals
                else actual_use_custom_templates[0]
            )

            if use_custom_templates:
                vals["body_arch"] = vals["body_arch_custom"]
                vals["body_html"] = vals["body_arch_custom"]
        super().write(vals)

    @api.onchange("mail_template_id")
    def _onchange_template_id(self):
        """
        Instanciate subject and body from template to model
        """
        tmpl = self.mail_template_id
        if tmpl:
            if tmpl.subject:
                self.subject = tmpl.subject
            if tmpl.body_html:
                self.body_arch = tmpl.body_html
                self.body_arch_custom = tmpl.body_html
                self.body_html = tmpl.body_html

    def save_as_template(self):
        self.ensure_one()
        template_name = "Mass Mailing: {subject}"
        values = {
            "name": template_name.format(subject=self.subject),
            "subject": self.subject or False,
            "body_html": self.body_arch or False,
        }
        template = self.env["mail.template"].create(values)
        self.mail_template_id = template
        self._onchange_template_id()
