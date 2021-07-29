# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class ChangeMainCoordinate(models.AbstractModel):
    _name = 'change.main.coordinate'
    _description = 'Change Main Coordinate Wizard'

    invalidate_previous_coordinate = fields.Boolean(
        'Invalidate Previous Main Coordinate',
    )
    change_allowed = fields.Boolean(
        default=True,
    )

    @api.multi
    def _get_discriminant_value(self, force_field=False):
        """
        Get the value of the discriminant field
        :param force_field: str
        :return: str, int, float, bool
        """
        self.ensure_one()
        coord_obj = self.env[self._get_target_model()]
        if coord_obj._is_discriminant_m2o():
            force_field = force_field or 'id'
            value = self[coord_obj._discriminant_field]
            return value[force_field]
        return self[coord_obj._discriminant_field]

    @api.model
    def view_init(self, fields_list):
        context = self.env.context
        target_model = self._get_target_model()
        if not target_model:
            raise exceptions.UserError(_('Target model not specified!'))
        active_model = context.get('active_model')
        if not active_model:
            raise exceptions.UserError(_('Active model not specified!'))
        active_ids = context.get('active_ids', context.get('res_id'))
        if not active_ids:
            raise exceptions.UserError(
                _('At least one partner is required to change its main '
                  'coordinate!'))
        return super().view_init(fields_list)

    @api.model
    def _get_target_model(self):
        target_model = self.env.context.get('target_model')
        if not target_model:
            target_model = self.env.context.get('active_model')
        return target_model

    @api.multi
    def button_change_main_coordinate(self):
        """
        Change main coordinate for a list of partners
        * a new main coordinate is created for each partner
        * the previous main coordinate is invalidates or not regarding
          the option ``invalidate_previous_coordinate``
        :raise: ERROR if no partner selected

        **Note**
        When launched from the partner form the partner id is taken ``res_id``
        :return: dict
        """
        self.ensure_one()
        context = self.env.context
        target_model = self._get_target_model()
        active_ids = context.get('active_ids', context.get('res_id'))
        active_model = context.get('active_model')
        active_obj = self.env[active_model]
        partners = targets = active_obj.browse(active_ids)
        if active_model != 'res.partner':
            partners = targets.mapped("partner_id")
        coordinate_value = self._get_discriminant_value()
        invalidate = self.invalidate_previous_coordinate
        target_obj = self.env[target_model]
        target_obj.with_context(invalidate=invalidate)._change_main_coordinate(
            partners, coordinate_value)
        return {}
