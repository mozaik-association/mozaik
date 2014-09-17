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
AVAILABLE_MONTHS = [7, 8, 9]


class pass_former_member(orm.TransientModel):

    _name = "pass.former.member"
    _description = 'Pass to former Member'

    def _get_selected_values(self, cr, uid, context=None):
        partner_obj = self.pool['res.partner']
        partner_ids = []
        concerned_partner_ids = []

        if context.get('active_domain'):
            active_domain = context.get('active_domain')
            partner_ids = partner_obj.search(
                cr, uid, active_domain, context=context)
        elif context.get('active_ids'):
            partner_ids = context.get('active_ids')

        if partner_ids:
            # search member with reference
            concerned_partner_ids = partner_obj.search(
                cr, uid, [('membership_state_id.code', '=', 'member'),
                          ('reference', '!=', False)],
                context=context)
        return partner_ids, concerned_partner_ids

    _columns = {
        'nb_selected': fields.integer('Selected Partners'),
        'nb_concerned': fields.integer('Concerned Partners'),
        'concerned_partner_ids': fields.text('IDS', required=True),
        'go': fields.boolean('Go')
    }

    def default_get(self, cr, uid, fields, context):
        """
        To get default values for the object.
        """
        res = super(pass_former_member, self).default_get(
            cr, uid, fields, context=context)
        if context is None:
            context = {}
        partner_ids, concerned_partner_ids = self._get_selected_values(
            cr, uid, context=context)
        res['nb_selected'] = len(partner_ids)
        res['nb_concerned'] = len(concerned_partner_ids)
        res['concerned_partner_ids'] = str(concerned_partner_ids)
        curr_month = date.today().month
        date_ok = curr_month in AVAILABLE_MONTHS
        res['go'] = date_ok and concerned_partner_ids

        return res

    def pass_former_member(self, cr, uid, ids, context=None):
        """
        Pass to former Member for all partner
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
            partner_ids = eval(wiz.concerned_partner_ids)
            session = ConnectorSession(cr, uid, context=context)
            if len(partner_ids) > worker_pivot:
                pass_former_member_action.delay(
                    session, self._name, partner_ids, context=context)
            else:
                pass_former_member_action(
                    session, self._name, partner_ids, context=context)


@job
def pass_former_member_action(session, model_name, partner_ids, context=None):
    """
    Pass to former Member for each partner
    """
    cr, uid, = session.cr, session.uid
    partner_obj = session.pool['res.partner']
    partner_obj.decline_payment(cr, uid, partner_ids, context=context)

    return
