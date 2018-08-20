# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ChangeMainPhone(models.TransientModel):
    _name = 'change.main.phone'
    _inherit = 'change.main.coordinate'
    _description = 'Change Main Phone Wizard'

    old_phone_id = fields.Many2one(
        "phone.phone",
        "Current main phone",
    )
    phone_id = fields.Many2one(
        "phone.phone",
        "New main phone",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
    )

    @api.model
    def default_get(self, fields_list):
        """
        Based on the context, fill the partner_id automatically.
        If the mode is switch, auto-fill the phone_id
        :param fields_list: list of str
        :return: dict
        """
        result = super(ChangeMainPhone, self).default_get(fields_list)
        context = self.env.context
        active_id = context.get('active_ids', context.get('active_id'))
        if active_id and isinstance(active_id, list):
            active_id = active_id[0]
        if context.get('mode') == 'switch':
            target_model = context.get('target_model')
            coordinate = self.env[target_model].browse(active_id)
            result.update({
                'phone_id': coordinate.phone_id.id,
                'partner_id': coordinate.partner_id.id,
            })
        else:
            result.update({
                'partner_id': active_id,
            })
        return result

    @api.onchange('partner_id', 'phone_id')
    def _onchange_phone_id(self):
        if self.phone_id.type == 'fix':
            self.old_phone_id = self.partner_id.fix_coordinate_id.phone_id.id
        elif self.phone_id.type == 'fax':
            self.old_phone_id = self.partner_id.fax_coordinate_id.phone_id.id
        else:
            self.old_phone_id = self.partner_id.mobile_coordinate_id\
                .phone_id.id
        self.change_allowed = not self.phone_id == self.old_phone_id
