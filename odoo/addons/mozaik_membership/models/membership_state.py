# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class MembershipState(models.Model):

    _name = 'membership.state'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership State'
    _order = 'name'
    _unicity_keys = 'code'

    name = fields.Char(string='Membership State', required=True,
                       track_visibility='onchange', translate=True)
    code = fields.Char(required=True)

    @api.model
    def _get_default_state(self, default_state=False):
        """
        :type default_state: string
        :param default_state: an other code of membership_state

        :rparam: id of a membership state with a default_code found into
            * ir.config.parameter's membership_state
            * default_state if not False

        **Note**
        default_state has priority
        """

        if not default_state:
            default_state = self.env['ir.config_parameter'].sudo().get_param(
                'default_membership_state', default='without_membership')

        state_ids = self.search([('code', '=', default_state)])

        return state_ids
