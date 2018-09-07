# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import first


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.model
    def _get_default_model(self):
        """
        Get the default model
        :return: ir.model recordset
        """
        return self.env.ref('mozaik_communication.model_email_coordinate')

    @api.model
    def _get_default_user(self):
        """
        Get the default user
        :return: res.users recordset
        """
        return self.env.user

    @api.model
    def _get_default_instance(self):
        #TODO: xxx
        return False
        return first(self.env.user.partner_id.int_instance_m2m_ids)

    # Fake field for auto-completing placeholder
    involvement_category_id = fields.Many2one(
        comodel_name='partner.involvement.category',
        string='Involvement Category',
        domain=[('code', '!=', False)],
    )
    res_users_ids = fields.Many2many(
        comodel_name='res.users',
        relation='email_template_res_users_rel',
        column1='template_id',
        column2='user_id',
        string='Owners',
        required=True,
        default=lambda s: s._get_default_user(),
    )
    int_instance_id = fields.Many2one(
        comodel_name='int.instance',
        string='Internal Instance',
        index=True,
        default=lambda s: s._get_default_instance(),
    )
    model_id = fields.Many2one(
        default=lambda s: s._get_default_model(),
    )

    @api.onchange('placeholder_id', 'involvement_category_id')
    def _onchange_placeholder_id(self):
        code_key = '{{CODE}}'
        for wizard in self:
            placeholder_value = wizard.placeholder_value or ''
            category = wizard.involvement_category_id
            if code_key in placeholder_value and category:
                placeholder_value = placeholder_value.replace(
                    code_key, category.code)
                wizard.placeholder_value = placeholder_value
