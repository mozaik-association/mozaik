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
from datetime import date
from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
import openerp.tools as tools

DEFAULT_STATE = 'without_membership'


class membership_membership_line(orm.Model):

    _name = 'membership.membership_line'
    _inherit = ['membership.membership_line', 'abstract.ficep.model']

    _inactive_cascade = True

    def _generate_membership_reference(self, cr, uid, membership_line_id,
                                       context=None):
        """
        This method will generate a membership reference for payment
        """
        mml = self.browse(cr, uid, membership_line_id, context=context)
        base_identifier = '0000000'
        identifier = '%s' % mml.partner.identifier
        base = '9%s%s' % (('%s' % date.today().year)[2:],
                          ''.join((base_identifier[:-len(identifier)],
                                   identifier)))
        comm_struct = '%s%s' % (base, int(base) % 97 or 97)
        return '+++%s/%s/%s+++' % (comm_struct[:3], comm_struct[3:7],
                                   comm_struct[7:])

    _columns = {
        'partner': fields.many2one(
            'res.partner', string='Member',
            ondelete='cascade', required=True, select=True),
        'membership_id': fields.many2one(
            'product.product', string='Membership Type',
            domain="[('membership', '!=', False), ('list_price', '>', 0.0)]",
            required=True, select=True),
        'membership_state_id': fields.many2one(
            'membership.state', string='State',
            select=True),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance',
            required=True, select=True),
        'reference': fields.char('Reference'),
    }

    _defaults = {
        'membership_id': lambda self, cr, uid, ids, context = None:
            self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'ficep_base', 'membership_product_free')[1],
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool.get('int.instance').get_default(cr, uid),
    }

    _order = 'date_from desc, date_to desc, partner'

# constraints

    _unicity_keys = 'partner'

    def init(self, cr):
        '''
        Inactivate odoo demo data incompatible
        with abstract ficep indexes mechanism
        '''
        if tools.config.options['test_enable']:
            cr.execute("UPDATE membership_membership_line "
                       "SET active = FALSE "
                       "WHERE membership_state_id IS NULL")

        # create expected index
        super(membership_membership_line, self).init(cr)

# orm methods

    def _where_calc(self, cr, user, domain, active_test=True, context=None):
        '''
        Read always inactive membership lines
        '''
        res = super(membership_membership_line, self)._where_calc(
            cr, user, domain, active_test=False, context=context)
        return res


class membership_state(orm.Model):

    _name = 'membership.state'
    _inherit = ['abstract.ficep.model']
    _description = 'Membership State'

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

    _columns = {
        'name': fields.char('Status', required=True,
                            track_visibility='onchange', translate=True),
        'code': fields.char('Code', required=True),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'code'
