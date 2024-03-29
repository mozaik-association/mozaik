# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first


class MailTemplate(models.Model):
    _name = "mail.template"
    _inherit = [
        "mail.template",
        "owner.mixin",
    ]

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
    # Owners come from mixin. Rename columns
    res_users_ids = fields.Many2many(
        relation="email_template_res_users_rel",
        column1="template_id",
        column2="user_id",
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

    @api.onchange("placeholder_id", "involvement_category_id")
    def _onchange_placeholder_id(self):
        code_key = "{{CODE}}"
        super()._onchange_placeholder_id()

        # Look for involvement category codes
        for record in self:
            placeholder_value = record.placeholder_value or ""
            category = record.involvement_category_id
            if code_key in placeholder_value and category:
                placeholder_value = placeholder_value.replace(code_key, category.code)
                record.placeholder_value = placeholder_value
