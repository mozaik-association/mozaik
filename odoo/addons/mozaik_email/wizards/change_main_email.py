# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ChangeMainEmail(models.TransientModel):
    _name = 'change.main.email'
    _inherit = 'change.main.coordinate'
    _description = 'Change Main Email Wizard'

    old_email = fields.Char(
        "Current main email",
    )
    email = fields.Char(
        "New main email",
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        """
        During this default_get, fill automatically (depending on context)
        email and old_email.
        :param fields_list: list of str
        :return: dict
        """
        result = super(ChangeMainEmail, self).default_get(fields_list)
        context = self.env.context
        if context.get('mode') == 'switch':
            target_model = context.get('active_model')
            target_id = context.get('active_id')
            target = self.env[target_model].browse(target_id)
            if hasattr(target, 'email'):
                result.update({
                    'email': target.email,
                })
        active_ids = context.get('active_ids', [context.get('active_id')])
        active_model = context.get('active_model')
        if active_model == 'res.partner' and len(active_ids) == 1:
            partner = self.env[active_model].browse(active_ids)
            result.update({
                'old_email': partner.email_coordinate_id.email,
            })
        return result
