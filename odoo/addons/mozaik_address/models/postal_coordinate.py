# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class PostalCoordinate(models.Model):

    _name = 'postal.coordinate'
    _inherit = ['abstract.coordinate']
    _description = 'Postal Coordinate'

    _discriminant_field = 'address_id'
    _trigger_fields = []
    _undo_redirect_action = 'mozaik_address.postal_coordinate_action'

    address_id = fields.Many2one(
        'address.address', string='Address', required=True,
        readonly=True, index=True)
    co_residency_id = fields.Many2one(
        'co.residency', string='Co-Residency', index=True)

    _rec_name = _discriminant_field

    _unicity_keys = 'partner_id, %s' % _discriminant_field

    @api.multi
    @api.onchange("unauthorized", "co_residency_id")
    def _onchange_unauthorized(self):
        self.ensure_one()
        if self.unauthorized and self.co_residency_id:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _(
                        'Unauthorizing a coordinate usually involves '
                        'a change in its co-residency.'
                    )
                }
            }
        return {}

    @api.multi
    def name_get(self):
        result = super().name_get()
        new_result = []
        for res in result:
            postal_coordinate = self.browse(res[0])
            name = res[1]
            if postal_coordinate.co_residency_id:
                name = "%s (%s)" % (
                    name, postal_coordinate.co_residency_id.display_name)
            new_result.append((res[0], name))
        return new_result

    @api.model
    def _get_fields_to_update(self, mode):
        """
        :type mode: char
        :param mode: mode defining return values
        :rtype: dictionary
        :rparam: values to update
        """
        res = super()._get_fields_to_update(mode)
        if mode in ['duplicate', 'reset']:
            res.update({'co_residency_id': False})
        return res
