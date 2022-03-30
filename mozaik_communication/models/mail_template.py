# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
from odoo.fields import first


class MailTemplate(models.Model):
    _inherit = "mail.template"

    @api.model
    def _get_default_model_id(self):
        """
        Get the default model
        :return: ir.model recordset
        """
        return self.env.ref("base.model_res_partner")

    @api.model
    def _get_default_res_users_ids(self):
        """
        Get the default user
        :return: res.users recordset
        """
        return self.env.user

    @api.model
    def _get_default_int_instance_id(self):
        return first(self.env.user.partner_id.int_instance_m2m_ids)

    # Fake field for auto-completing placeholder
    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement Category",
        domain=[("code", "!=", False)],
    )
    res_users_ids = fields.Many2many(
        comodel_name="res.users",
        relation="email_template_res_users_rel",
        column1="template_id",
        column2="user_id",
        string="Owners",
        default=lambda s: s._get_default_res_users_ids(),
    )
    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal Instance",
        index=True,
        default=lambda s: s._get_default_int_instance_id(),
    )
    model_id = fields.Many2one(
        default=lambda s: s._get_default_model_id(),
    )

    @api.constrains("res_users_ids")
    def _check_res_users_ids_not_empty(self):
        """
        res_users_ids is not required otherwise it causes problems
        with record rules on res.partner, but we want at least
        one owner for each mail.template.
        """
        for template in self:
            owners = template.sudo().read(["res_users_ids"])
            if len(owners) == 0:
                raise exceptions.ValidationError(
                    _("Please add a (non archived) owner for this mail template.")
                )

    @api.onchange("placeholder_id", "involvement_category_id")
    def _onchange_placeholder_id(self):
        code_key = "{{CODE}}"
        for wizard in self:
            placeholder_value = wizard.placeholder_value or ""
            category = wizard.involvement_category_id
            if code_key in placeholder_value and category:
                placeholder_value = placeholder_value.replace(code_key, category.code)
                wizard.placeholder_value = placeholder_value
