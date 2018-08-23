# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class membership_state(orm.Model):

    _name = 'membership.state'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership State'
    _unicity_keys = 'code'
    _order = 'name'

    _columns = {
        'name': fields.char('Membership State', required=True,
                            track_visibility='onchange', translate=True),
        'code': fields.char('Code', required=True),
    }

    def _state_default_get(self, cr, uid, default_state=False, context=None):
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
            default_state = self.pool['ir.config_parameter'].get_param(
                cr, uid,
                'default_membership_state', default='without_membership',
                context=context)

        state_ids = self.search(
            cr, uid, [('code', '=', default_state)], context=context)

        return state_ids and state_ids[0] or False
