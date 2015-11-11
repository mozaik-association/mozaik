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
from datetime import date

from openerp.osv import orm, fields
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

WORKER_PIVOT = 10
AVAILABLE_MONTHS = [7, 8, 9]


class pass_former_member(orm.TransientModel):

    _name = "pass.former.member"
    _description = 'Wizard to Transform Members to Former Members'

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
            domain = [('id', 'in', partner_ids), ('reference', '!=', False)]
            concerned_partner_ids = partner_obj.search(
                cr, uid, domain, context=context)
            data = partner_obj.read_group(
                cr, uid, domain,
                ['membership_state_id'], ['membership_state_id'],
                context=context, orderby='membership_state_id ASC')
            concerned_partners = [
                '%s: %s' % (st['membership_state_id'][1],
                            st['membership_state_id_count'])
                for st in data if st['membership_state_id']
            ]
            concerned_partners = '\n'.join(concerned_partners)
        return partner_ids, concerned_partner_ids, concerned_partners

    _columns = {
        'nb_selected': fields.integer('Selected Partners'),
        'concerned_members': fields.text('Concerned Members'),
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
        partner_ids, concerned_partner_ids, concerned_members = \
            self._get_selected_values(cr, uid, context=context)
        res['nb_selected'] = len(partner_ids)
        res['concerned_members'] = concerned_members
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
            if len(partner_ids) > worker_pivot:
                session = ConnectorSession(cr, uid, context=context)
                pass_former_member_action.delay(
                    session, self._name, partner_ids, context=context)
            else:
                do_pass_former_member_action(
                    self.pool['res.partner'], cr, uid,
                    partner_ids, context=context)


@job
def pass_former_member_action(session, model_name, partner_ids, context=None):
    """
    Pass to former Member for each partner
    """
    cr, uid, = session.cr, session.uid
    partner_obj = session.pool['res.partner']
    do_pass_former_member_action(
        partner_obj, cr, uid, partner_ids, context=context)


def do_pass_former_member_action(obj, cr, uid, partner_ids, context=None):
    """
    Pass to former Member for each partner
    Reset reference for each other
    """
    obj.decline_payment(cr, uid, partner_ids, context=context)
    domain = [('id', 'in', partner_ids), ('reference', '!=', False)]
    ids = obj.search(cr, uid, domain, context=context)
    if ids:
        obj.write(cr, uid, ids, {'reference': False}, context=context)
    pass
