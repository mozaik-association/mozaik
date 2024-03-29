# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo import _, api, fields, models
from odoo.tools import formataddr


class DistributionListMassFunction(models.TransientModel):
    _name = "distribution.list.mass.function"
    _description = "Mass Function"

    def _get_e_mass_function(self):
        """
        Get available mass functions for mode=email.coordinate
        :return:
        """
        funcs = [
            ("csv", _("CSV Extraction")),
        ]
        return funcs

    def _get_default_e_mass_function(self):
        """
        Get default email.coordinate mass function
        :return:
        """
        funcs = self._get_e_mass_function()
        return funcs[0][0]

    trg_model = fields.Selection(
        selection=[
            ("email.coordinate", "Email Coordinate"),
            ("postal.coordinate", "Postal Coordinate"),
        ],
        string="Sending mode",
        required=True,
        default="email.coordinate",
    )
    e_mass_function = fields.Selection(
        selection=_get_e_mass_function,
        string="Mass function (Email)",
        default=lambda self: self._get_default_e_mass_function(),
    )
    p_mass_function = fields.Selection(
        selection=[
            ("csv", "CSV Extraction"),
        ],
        string="Mass function (Postal)",
        default="csv",
    )
    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list",
        string="Distribution List",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.context.get("active_id", False),
    )
    subject = fields.Char()
    body = fields.Html(
        string="Content",
        help="Automatically sanitized HTML contents",
    )
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="distribution_list_mass_function_ir_attachment_rel",
        column1="wizard_id",
        column2="attachment_id",
        string="Attachments",
    )
    mass_mailing_name = fields.Char()
    sort_by = fields.Selection(
        selection=[
            ("identifier", "Identification Number"),
            ("technical_name", "Name"),
            ("country_id, zip, technical_name", "Zip Code"),
        ],
    )
    email_bounce_counter = fields.Integer(
        string="Maximum of fails",
    )
    include_email_bounced = fields.Boolean(
        default=False, string="Include email bounced"
    )
    include_postal_bounced = fields.Boolean(
        default=False, string="Include postal bounced"
    )
    internal_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal instance",
        ondelete="cascade",
    )
    include_without_coordinate = fields.Boolean(
        default=False,
    )
    groupby_coresidency = fields.Boolean(
        string="Group by co-residency",
        default=False,
    )
    export_file = fields.Binary(
        string="File",
        readonly=True,
    )
    export_filename = fields.Char()
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
    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement Category",
        domain=[("code", "!=", False)],
    )
    partner_from_id = fields.Many2one(
        comodel_name="res.partner",
        string="From",
        domain=lambda self: self._get_domain_partner_from_id(),
        default=lambda self: self._get_default_partner_from_id(),
        context={"show_email": 1},
    )
    partner_name = fields.Char()
    email_from = fields.Char(
        compute="_compute_email_from",
    )
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
    )

    @api.depends("partner_from_id", "partner_name")
    def _compute_email_from(self):
        for wz in self:
            name = ""
            email = ""
            if wz.partner_from_id:
                name = wz.partner_from_id.name
                email = wz.partner_from_id.email or ""
            if wz.partner_name:
                name = wz.partner_name.strip()
            wz.email_from = formataddr((name, email))

    @api.onchange("trg_model")
    def _onchange_trg_model(self):
        """
        Reset some fields when `trg_model` change
        """
        if self.trg_model == "postal.coordinate":
            self.e_mass_function = False
            self.p_mass_function = self._fields["p_mass_function"].selection[0][0]
        if self.trg_model == "email.coordinate":
            self.e_mass_function = self._get_default_e_mass_function()
            self.p_mass_function = False

    @api.onchange("e_mass_function")
    def _onchange_e_mass_function(self):
        """
        Reset some fields when `mass_function` change
        """
        self.export_filename = False
        self.include_without_coordinate = False

    @api.onchange("subject")
    def _onchange_subject(self):
        """
        Propose a default value for the mass mailing name
        """
        if not self.mass_mailing_name:
            self.mass_mailing_name = self.subject

    def mass_function(self):
        """
        This method allow to make mass function on
        - email.coordinate
        - postal.coordinate
        """
        self.ensure_one()
        context = self.env.context.copy()
        main_domain = []
        if self.internal_instance_id:
            main_domain.append(
                ("partner_instance_ids", "child_of", self.internal_instance_id.ids)
            )
        context.update(
            {
                "main_object_domain": main_domain,
            }
        )
        fct = self.e_mass_function
        if self.trg_model != "email.coordinate":
            fct = self.p_mass_function
        if fct == "csv" and self.include_without_coordinate:
            context.update(
                {
                    "active_test": False,
                    "alternative_object_field": "partner_id",
                    "alternative_target_model": self.distribution_list_id.dst_model_id.model,
                    "alternative_object_domain": main_domain,
                }
            )
        if self.sort_by:
            context.update(
                {
                    "sort_by": self.sort_by,
                }
            )

        self_ctx = self.with_context(context)
        if self.trg_model == "email.coordinate":
            alternatives, mains = self_ctx._mass_email_coordinate(fct, main_domain)
        elif self.trg_model == "postal.coordinate":
            alternatives, mains = self_ctx._mass_postal_coordinate(fct, main_domain)

        if fct == "csv":
            if self.include_without_coordinate:
                self_ctx.export_csv("res.partner", alternatives)
            else:
                self_ctx.export_csv("res.partner", mains, self.groupby_coresidency)

            return {
                "name": _("Mass Function"),
                "type": "ir.actions.act_window",
                "res_model": "distribution.list.mass.function",
                "view_mode": "form",
                "view_type": "form",
                "res_id": self.id,
                "views": [(False, "form")],
                "target": "new",
            }
        return {}

    def _mass_postal_coordinate(self, fct, main_domain):
        """
        Manage mass function when the target model is postal.coordinate
        :param fct: str
        :param main_domain: list (domain)
        :return: tuple of 2 recordset
        """
        if not self.include_postal_bounced:
            if self.distribution_list_id.dst_model_id.model in [
                "virtual.target",
                "res.partner",
            ]:
                main_domain.append(("postal_bounced", "=", False))

        main_object_field = (
            "partner_id"
            if self.distribution_list_id.dst_model_id.model == "virtual.target"
            else "id"
        )
        self = self.with_context(
            main_target_model="res.partner",
            main_object_field=main_object_field,
        )
        if fct == "csv":
            # Get CSV containing postal coordinates
            dl = self.distribution_list_id
            mains, alternatives = dl._get_complex_distribution_list_ids()
        return alternatives, mains

    def _mass_email_coordinate(self, fct, main_domain):
        """
        Manage mass function when the target model is email.coordinate
        :param fct: str
        :param main_domain: list (domain)
        :return: tuple of 2 recordset
        """
        dst_model = self.distribution_list_id.dst_model_id.model

        if dst_model == "virtual.target":
            if self.include_email_bounced:
                main_domain.append(
                    ("email_bounce_counter", "<=", max([self.email_bounce_counter, 0]))
                )
            else:
                main_domain.append(("email_bounce_counter", "=", 0))
        elif dst_model == "res.partner":
            if self.include_email_bounced:
                main_domain.append(
                    ("email_bounced", "<=", max([self.email_bounce_counter, 0]))
                )
            else:
                main_domain.append(("email_bounced", "=", 0))

        model_contact = self.env["ir.model"].search([("model", "=", "res.partner")])
        main_object_field = (
            "id"
            if self.distribution_list_id.dst_model_id == model_contact
            else "partner_id"
        )
        self = self.with_context(
            main_object_field=main_object_field,
            main_target_model="res.partner",
        )
        if fct == "csv":
            # Get CSV containing email coordinates
            dl = self.distribution_list_id
            mains, alternatives = dl._get_complex_distribution_list_ids()
        return alternatives, mains

    def export_csv(self, model, targets, group_by=False):
        """
        Export the specified coordinates to a CSV file.
        :param model: str
        :param targets: recordset
        :param group_by: bool
        :return: bool
        """
        csv_content = self.env["export.csv"]._get_csv(
            model, targets.ids, group_by=group_by
        )
        csv_content = base64.encodebytes(csv_content.encode())
        return self.write(
            {
                "export_file": csv_content,
                "export_filename": "extract.csv",
            }
        )

    @api.model
    def _get_domain_partner_from_id(self):
        """
        Load partners and transform results into a domain
        :return: list (domain)
        """
        default_dist_list_id = self._context.get("default_distribution_list_id", False)
        if not default_dist_list_id:
            return []
        dst_list = self.env["distribution.list"].browse(default_dist_list_id)
        partners = dst_list._get_partner_from()
        return [("id", "in", partners.ids)]

    @api.model
    def _get_default_partner_from_id(self):
        """

        :return: res.partner recordset
        """
        default_dist_list_id = self._context.get("default_distribution_list_id", False)
        if not default_dist_list_id:
            return []
        dst_list = self.env["distribution.list"].browse(default_dist_list_id)
        if self.env.user.partner_id in dst_list._get_partner_from():
            return self.env.user.partner_id
        return self.env["res.partner"].browse()

    @api.onchange("mail_template_id")
    def _onchange_template_id(self):
        """
        Instanciate subject and body from template to wizard
        """
        tmpl = self.mail_template_id
        if tmpl:
            if tmpl.subject:
                self.subject = tmpl.subject
            if tmpl.body_html:
                self.body = tmpl.body_html

    @api.onchange("placeholder_id", "involvement_category_id")
    def _onchange_placeholder_id(self):
        code_key = "{{CODE}}"
        for wizard in self:
            if wizard.placeholder_id:
                placeholder_value = wizard.placeholder_id.placeholder
                wizard.placeholder_id = False
                if code_key in placeholder_value and wizard.involvement_category_id:
                    placeholder_value = placeholder_value.replace(
                        code_key, wizard.involvement_category_id.code
                    )
                wizard.placeholder_value = placeholder_value
