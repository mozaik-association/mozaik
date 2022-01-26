# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailingMailing(models.Model):

    _inherit = "mailing.mailing"

    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
    )

    @api.model
    def create(self, vals):
        mass_mailing_from_mass_action = self._context.get(
            "mass_mailing_from_mass_action", False
        )
        vals_to_add = {}
        if (
            mass_mailing_from_mass_action
            and "body_html" in vals
            and "body_arch" not in vals
        ):
            vals_to_add["body_arch"] = vals["body_html"]
        elif "body_arch" in vals:
            vals_to_add["body_html"] = vals["body_arch"]

        if vals_to_add.keys():
            vals.update(vals_to_add)
        return super().create(vals)

    def write(self, vals):
        if "body_arch" in vals:
            vals["body_html"] = vals["body_arch"]
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
                self.body_html = tmpl.body_html

    def save_as_template(self):
        self.ensure_one()
        template_name = u"Mass Mailing: {subject}"
        values = {
            "name": template_name.format(subject=self.subject),
            "subject": self.subject or False,
            "body_html": self.body_arch or False,
        }
        template = self.env["mail.template"].create(values)
        self.mail_template_id = template
        self._onchange_template_id()
