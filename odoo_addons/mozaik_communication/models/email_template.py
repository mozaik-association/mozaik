# -*- coding: utf-8 -*-
# © 2018 ACSONE SA/NV <https://acsone.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    @api.model
    def _get_default_model_id(self):
        return self.env['ir.model'].search(
            [('model', '=', 'email.coordinate')])

    @api.model
    def _get_default_res_users_ids(self):
        return self.env.user

    @api.model
    def _get_default_instance_id(self):
        instances = self.env.user.partner_id.int_instance_m2m_ids
        return instances and instances[0] or False

    # Fake field for auto-completing placeholder
    involvement_category_id = fields.Many2one(
        'partner.involvement.category', string='Involvement Category',
        domain=[('code', '!=', False)])

    res_users_ids = fields.Many2many(
        comodel_name='res.users', relation='email_template_res_users_rel',
        column1='template_id', column2='user_id',
        string='Owners', required=True,
        default=lambda s: s._get_default_res_users_ids())
    int_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Internal Instance', index=True,
        default=lambda s: s._get_default_instance_id())
    model_id = fields.Many2one(
        default=lambda s: s._get_default_model_id())

    @api.onchange('placeholder_id', 'involvement_category_id')
    def _onchange_placeholder_id(self):
        super(EmailTemplate, self)._onchange_placeholder_id()
        for wizard in self:
            placeholder_value = wizard.placeholder_value
            if placeholder_value and '{{CODE}}' in placeholder_value \
               and wizard.involvement_category_id:
                placeholder_value = placeholder_value.replace(
                    '{{CODE}}', wizard.involvement_category_id.code)
                wizard.placeholder_value = placeholder_value
