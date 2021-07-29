# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class ChangePhoneType(models.TransientModel):
    _name = 'change.phone.type'
    _description = "Change Phone Type Wizard"

    @api.model
    def _selection_type(self):
        """
        Get selection available for phone.phone type field
        :return: list of tuple (selection choices)
        """
        return self.env['phone.phone']._fields['type'].selection

    phone_id = fields.Many2one(
        "phone.phone",
        'Phone',
        readonly=True,
    )
    is_main = fields.Boolean(
        'Set as main',
        default=True,
    )
    type = fields.Selection(
        _selection_type,
    )

    @api.model
    def default_get(self, fields_list):
        result = super(ChangePhoneType, self).default_get(fields_list)
        context = self.env.context
        active_model = context.get('active_model', False)
        if active_model:
            active_id = context.get('active_id', context.get('active_ids'))
            if active_id and isinstance(active_id, list):
                active_id = active_id[0]
            phone = self.env[active_model].browse(active_id)
            result.update({
                'phone_id': phone.id,
            })
        return result

    @api.multi
    def change_phone_type(self):
        """
        Action to change the phone type
        """
        self.ensure_one()
        if self.type == self.phone_id.type:
            raise exceptions.UserError(
                _('New phone type should be different than current one!'))

        self.phone_id.phone_coordinate_ids.ensure_one_main_coordinate(
            invalidate=False)
        self.phone_id.write({
            'type': self.type,
        })
        phone_coordinates = self.phone_id.phone_coordinate_ids
        if not self.is_main:
            phone_coordinates.write({
                'is_main': False,
            })
        phone_coordinates = phone_coordinates.filtered(lambda c: c.is_main)
        wizard_obj = self.env['change.main.phone']
        for coordinate in phone_coordinates:
            context = self.env.context.copy()
            context.update({
                'active_model': coordinate._name,
                'target_model': coordinate._name,
                'mode': 'switch',
                'active_id': coordinate.id,
                'active_ids': coordinate.ids,
            })
            wizard = wizard_obj.with_context(context).create({})
            wizard.button_change_main_coordinate()
