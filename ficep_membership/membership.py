# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tools import logging
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)
DEFAULT_STATE = 'without_membership'


class membership_membership_line(orm.Model):

    _name = 'membership.membership_line'
    _inherit = ['membership.membership_line', 'abstract.ficep.model']

    _columns = {
        'membership_state_id': fields.many2one('membership.state', 'State'),
    }

    defaults = {
        'membership_state_id': lambda self, cr, uid, ids, c: \
                self.pool['membership.state']._state_default_get(cr, uid, context=c),
    }

    _unicity_keys = 'N/A'


class membership_state(orm.Model):

    def _state_default_get(self, cr, uid, other_default_state=False, context=None):
        """
        ==================
        _state_default_get
        ==================
        :type other_default_state: string
        :param other_default_state: an other code of membership_state

        :rparam: id of a membership state with a default_code found into
            * ir.config.parameter's default_membership_state
            * other_default_state if not False

        **Note**
        other_default_state has priority
        """

        if other_default_state:
            parameter_obj = self.pool['ir.config.parameter']
            parameter_ids = parameter_obj.search(cr, uid, [('default_membership_state', '=', DEFAULT_STATE)],
                                                                context=context)
            if parameter_ids:
                other_default_state = parameter_obj.read(cr, uid, parameter_ids[0], context=context)['default_membership_state']

        state_ids = self.search(cr, uid, [('code', '=', other_default_state)], context=context)
        return state_ids and state_ids[0] or False

    _name = 'membership.state'
    _inherit = ['abstract.ficep.model']
    _description = 'Membership State'

    _columns = {
        'name': fields.char('Status', required=True, track_visibility='onchange'),
        'code': fields.char('Code', required=True, track_visibility='onchange'),
    }

    _unicity_keys = 'code'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
