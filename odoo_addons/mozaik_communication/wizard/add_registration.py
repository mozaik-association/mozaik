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
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.osv import orm, fields

WORKER_PIVOT = 10


class add_registration(orm.TransientModel):

    _name = 'add.registration'
    _description = 'Add Registrations'

    _columns = {
        'event_id': fields.many2one(
            'event.event', string="Event"),
        'distribution_list_id': fields.many2one(
            'distribution.list', string="Distribution List")
    }

    _defaults = {
        'event_id': lambda self, cr, uid, context:
            context.get('active_id', False),
    }

    def add_registration(self, cr, uid, ids, context=None):
        '''
        Generate event registration from the partner_ids extracted from
        the distribution list
        '''
        try:
            parameter_obj = self.pool['ir.config_parameter']
            worker_pivot = int(parameter_obj.get_param(
                cr, uid, 'worker_pivot', WORKER_PIVOT))
        except:
            worker_pivot = WORKER_PIVOT
        for wiz in self.browse(cr, uid, ids, context=context):
            dl_obj = self.pool['distribution.list']
            ctx = dict(context or {},
                       main_object_field='partner_id',
                       main_target_model='res.partner')
            partner_ids = dl_obj.get_complex_distribution_list_ids(
                cr, uid, [wiz.distribution_list_id.id], context=ctx)[0]
            session = ConnectorSession(cr, uid, context=context)
            if len(partner_ids) > worker_pivot:
                add_registration_action.delay(
                    session, self._name, wiz.event_id.id, partner_ids,
                    context=context)
            else:
                add_registration_action(
                    session, self._name, wiz.event_id.id, partner_ids,
                    context=context)


@job
def add_registration_action(
        session, model_name, event_id, partner_ids, context=None):
    """
    create event registration for each partner
    """
    self, cr, uid = session, session.cr, session.uid
    vals = {
        'event_id': event_id,
    }
    reg_obj = self.pool['event.registration']
    ev_obj = self.pool['event.event']
    reg_ids = ev_obj.read(
        cr, uid, event_id, ['registration_ids'],
        context=context)['registration_ids']
    if reg_ids:
        reg_vals = reg_obj.read(
            cr, uid, reg_ids, ['partner_id'], context=context)
        # do not try to create registration two registration for the same
        # partner (partner_id, event_id)
        found_p_ids = []
        for reg_val in reg_vals:
            if reg_val.get('partner_id', False):
                found_p_ids.append(reg_val['partner_id'][0])

        partner_ids = list(set(partner_ids) - set(found_p_ids))
    for p_id in partner_ids:
        vals['partner_id'] = p_id
        reg_obj.create(cr, uid, vals, context=context)
    return
