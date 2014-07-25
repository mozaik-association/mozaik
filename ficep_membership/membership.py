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
from datetime import date

_logger = logging.getLogger(__name__)
DEFAULT_STATE = 'without_membership'


class membership_membership_line(orm.Model):

    _name = 'membership.membership_line'
    _inherit = ['membership.membership_line', 'abstract.ficep.model']

    _order = 'date_from desc'

    def _generate_membership_reference(self, cr, uid, membership_line_id, context=None):
        """
        ==============================
        _generate_membership_reference
        ==============================
        """
        mml = self.browse(cr, uid, membership_line_id, context=context)
        base_identifier = '0000000'
        identifier = '%s' % mml.partner.identifier
        base = '9%s%s' % (('%s' % date.today().year)[2:], ''.join((base_identifier[:-len(identifier)], identifier)))
        comm_struct = '%s%s' % (base, int(base) % 97 or 97)
        return '+++%s/%s/%s+++' % (comm_struct[:3], comm_struct[3:7], comm_struct[7:])

    _columns = {
        'partner': fields.many2one('res.partner', 'Partner', ondelete='cascade', select=1, required=True),
        'membership_id': fields.many2one('product.product', string="Membership"),
        'membership_state_id': fields.many2one('membership.state', type='many2one', string='State'),
        'is_current': fields.boolean('Is Current'),
    }

    _defaults = {
        'is_current': True,
    }

    _unicity_keys = 'N/A'


class membership_state(orm.Model):

    def _state_default_get(self, cr, uid, default_state=False, context=None):
        """
        ==================
        _state_default_get
        ==================
        :type default_state: string
        :param default_state: an other code of membership_state

        :rparam: id of a membership state with a default_code found into
            * ir.config.parameter's membership_state
            * default_state if not False

        **Note**
        default_state has priority
        """

        if not default_state:
            parameter_obj = self.pool['ir.config_parameter']
            parameter_ids = parameter_obj.search(cr, uid, [('key', '=', 'default_membership_state')], context=context)
            if parameter_ids:
                default_state = parameter_obj.read(cr, uid, parameter_ids[0], context=context)['value']

        state_ids = self.search(cr, uid, [('code', '=', default_state)], context=context)
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
