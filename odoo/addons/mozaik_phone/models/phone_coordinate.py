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
