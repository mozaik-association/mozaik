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

from openerp.osv import orm, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

WORKER_PIVOT = 10
AVAILABLE_MONTHS = [1]


class generate_reference(orm.TransientModel):

    _name = "generate.reference"
    _description = 'Generate Reference'

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
                           'member_candidate'),
                          ('id', 'in', partner_ids),
                          ],
                context=context)
        return partner_ids, member_ids, candidate_ids, former_ids

    _columns = {
        'nb_selected': fields.integer('Selected Partners'),
        'nb_member_concerned': fields.integer('Concerned Member'),
        'nb_candidate_concerned': fields.integer('Concerned Candidate Member'),
        'nb_former_concerned': fields.integer('Concerned Former Member'),
        'partner_ids': fields.text('IDS', required=True),
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
        concerned_ids = member_ids+candidate_ids
        res['partner_ids'] = str(concerned_ids)
        curr_month = date.today().month
        date_ok = curr_month in AVAILABLE_MONTHS
        res['go'] = date_ok and concerned_ids

        return res

    def generate_reference(self, cr, uid, ids, context=None):
        """
        Generate reference for all partner
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
                    session, self._name, partner_ids, context=context)
            else:
                generate_reference_action(
                    session, self._name, partner_ids, context=context)


@job
def generate_reference_action(session, model_name, partner_ids, context=None):
    """
    generate reference for each partner
    """
    cr, uid, = session.cr, session.uid
    partner_obj = session.pool['res.partner']
    for partner_id in partner_ids:
        ref = partner_obj._generate_membership_reference(
            cr, uid, partner_id, context=context)
        vals = {
            'reference': ref,
        }
        partner_obj.write(cr, uid, [partner_id], vals, context=context)

    return
