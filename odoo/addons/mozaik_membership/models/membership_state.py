# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class MembershipState(models.Model):

    _name = 'membership.state'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership State'
    _order = 'sequence, name'
    _unicity_keys = 'code'

    name = fields.Char(string='Membership State', required=True,
                       track_visibility='onchange', translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(
        help="Sequence used to define the membership state of partners",
        default=10,
    )

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

        state_id = self.search([('code', '=', default_state)], limit=1)

        return state_id

    @api.model
    def _get_by_code(self, code):
        """
        Get a membership.state by given code
        :param code: str
        :return: membership.state recordset
        """
        if not code:
            return self.browse()
        domain = [
            ('code', '=', code),
        ]
        return self.search(domain, limit=1)

    @api.model
    def _get_exclusion_state(self, lines=False):
        """
        Depending on previous lines, get the expulsion state
        :param lines: membership.line recordset
        :return: membership.state recordset
        """
        if lines:
            return self._get_by_code('expulsion_former_member')
        return self._get_by_code('inappropriate_former_member')

    @api.model
    def _get_all_exclusion_states(self):
        """
        Get every possible expulsion states
        :return: membership.state recordset
        """
        codes = [
            'expulsion_former_member',
            'inappropriate_former_member',
        ]
        domain = [
            ('code', 'in', codes),
        ]
        return self.search(domain)
