# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PhoneCoordinate(models.Model):
    _name = 'phone.coordinate'
    _inherit = ['abstract.coordinate']
    _description = 'Phone Coordinate'

    _discriminant_field = 'phone_id'
    _undo_redirect_action = 'mozaik_phone.phone_coordinate_act_window'
    _unicity_keys = 'partner_id, phone_id'
    _rec_name = _discriminant_field

    phone_id = fields.Many2one(
        'phone.phone',
        'Phone',
        required=True,
        readonly=True,
        index=True,
    )
    coordinate_type = fields.Selection(
        related='phone_id.type',
        readonly=True,
        store=True,
        default=False  # remove the default defined in abstract.coordinate
    )
    also_for_fax = fields.Boolean(
        related='phone_id.also_for_fax',
        readonly=True,
        store=True
    )

    @api.model
    def _get_coordinate_type_from_phone_id(self, phone_id):
        """
        Get the coordinate_type corresponding to the given phone id
        :param phone_id: int
        :return: str
        """
        return self.env['phone.phone'].browse(phone_id).type

    @api.model
    def _get_default_coordinate_type(self, values):
        """
        Get the default coordinate type.
        Useful for inherit
        :param values: dict
        :return: str
        """
        phone_id = values.get('phone_id')
        return self._get_coordinate_type_from_phone_id(phone_id)

    @api.model
    def _check_must_be_main(self, values):
        """
        Inherit the function because the coordinate_type comes from the
        phone_id.
        We don't need to call the super because the behaviour is different.
        If we call the super, we have to put is_main to False first
        :param values: dict
        :return: bool
        """
        partner_id = values.get('partner_id')
        phone_id = values.get('phone_id')
        coordinate_type = self._get_coordinate_type_from_phone_id(phone_id)
        domain = self.get_target_domain(partner_id, coordinate_type)
        coordinates = self.search_count(domain)
        if not coordinates:
            values.update({
                'is_main': True,
            })
        return True
