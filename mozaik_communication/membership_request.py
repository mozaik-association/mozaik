# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm


class membership_request(orm.Model):

    _inherit = 'membership.request'

    def _act_membership_state(
            self, cr, uid, membership_code, partner_id, context=None):
        '''
        If without membership
        :type membership_code: char
        :param membership_code: status code of a `membership.state`
        '''
        if membership_code == 'without_membership':
            self.pool['mail.mass_mailing.list'].generate_recipents(
                cr, uid, partner_id, context=context)
