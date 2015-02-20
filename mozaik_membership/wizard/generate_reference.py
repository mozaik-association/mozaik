# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import date

from openerp.osv import orm, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

_logger = logging.getLogger(__name__)

WORKER_PIVOT = 10


def get_year_selection():
    curr_year = date.today().year
    return [('%s' % str(curr_year+n), '%s' %
             str(curr_year+n)) for n in xrange(2)]


class generate_reference(orm.TransientModel):

    _name = "generate.reference"
    _description = 'Generate References'

    def _get_selected_values(self, cr, uid, context=None):
        partner_obj = self.pool['res.partner']
        partner_ids = []
        member_ids = []
        candidate_ids = []
        former_ids = []

        if context.get('active_domain'):
            active_domain = context.get('active_domain')
            partner_ids = partner_obj.search(
                cr, uid, active_domain, context=context)
        elif context.get('active_ids'):
            partner_ids = context.get('active_ids')

        if partner_ids:
            # search member with reference
            member_ids = partner_obj.search(
                cr, uid, [('membership_state_id.code', '=', 'member'),
                          ('id', 'in', partner_ids),
                          ],
                context=context)
            candidate_ids = partner_obj.search(
                cr, uid, [('membership_state_id.code', '=',
                           'member_candidate'),
                          ('id', 'in', partner_ids),
                          ],
                context=context)
            former_ids = partner_obj.search(
                cr, uid, [('membership_state_id.code', '=',
                           'former_member'),
                          ('id', 'in', partner_ids),
                          ],
                context=context)
        return partner_ids, member_ids, candidate_ids, former_ids

    _columns = {
        'nb_selected': fields.integer('Selected Partners'),
        'nb_member_concerned': fields.integer('Members'),
        'nb_candidate_concerned': fields.integer('Member Candidates'),
        'nb_former_concerned': fields.integer('Former Members'),
        'partner_ids': fields.text('IDS', required=True),
        'reference_date': fields.selection(get_year_selection(),
                                           string='Year'),
        'go': fields.boolean('Go')
    }

    def default_get(self, cr, uid, fields, context):
        """
        To get default values for the object.
        """
        res = super(generate_reference, self).default_get(
            cr, uid, fields, context=context)
        if context is None:
            context = {}
        partner_ids, member_ids, candidate_ids, former_ids = \
            self._get_selected_values(cr, uid, context=context)

        res['nb_selected'] = len(partner_ids)
        res['nb_member_concerned'] = len(member_ids)
        res['nb_candidate_concerned'] = len(candidate_ids)
        res['nb_former_concerned'] = len(former_ids)
        concerned_ids = member_ids+candidate_ids+former_ids
        res['partner_ids'] = str(concerned_ids)
        res['go'] = (len(concerned_ids) > 0)
        month = date.today().month
        year = date.today().year
        res['reference_date'] = str(month == 12 and year+1 or year)

        return res

    def generate_reference(self, cr, uid, ids, context=None):
        """
        Generate reference for all partners
        If concerned partner number is > to the ir.parameter value then
        call connector to delay this work
        **Note**
        ir.parameter or `WORKER_PIVOT`
        """

        try:
            parameter_obj = self.pool['ir.config_parameter']
            worker_pivot = int(parameter_obj.get_param(
                cr, uid, 'worker_pivot', WORKER_PIVOT))
        except:
            worker_pivot = WORKER_PIVOT
        for wiz in self.browse(cr, uid, ids, context=context):
            partner_ids = eval(wiz.partner_ids)
            session = ConnectorSession(cr, uid, context=context)
            if len(partner_ids) > worker_pivot:
                generate_reference_action.delay(
                    session, self._name, partner_ids, wiz.reference_date,
                    context=context)
            else:
                generate_reference_action(
                    session, self._name, partner_ids, wiz.reference_date,
                    context=context)


@job
def generate_reference_action(
        session, model_name, partner_ids, ref_date, context=None):
    """
    Generate reference for each partner
    """
    cr, uid, = session.cr, session.uid
    partner_obj = session.pool['res.partner']
    for partner_id in partner_ids:
        ref = partner_obj._generate_membership_reference(
            cr, uid, partner_id, ref_date, context=context)
        vals = {
            'reference': ref,
            'del_mem_card_date': False,
        }
        partner_obj.write(cr, uid, [partner_id], vals, context=context)
        _logger.info(
            'Reference %s generated for partner [%s]' % (ref, partner_id))

    return
