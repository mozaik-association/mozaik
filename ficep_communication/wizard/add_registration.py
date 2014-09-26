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
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.osv import orm, fields

WORKER_PIVOT = 10


class add_registration(orm.TransientModel):

    _name = 'add.registration'
    _description = 'Add Registration'

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
            if context is None:
                context = {}
            context['field_main_object'] = 'partner_id'
            partner_ids = dl_obj.get_complex_distribution_list_ids(
                cr, uid, [wiz.distribution_list_id.id], context=context)[0]
            session = ConnectorSession(cr, uid, context=context)
            if partner_ids > worker_pivot:
                add_registration_action.delay(
                    session, self._name, wiz.event_id.id, partner_ids,
                    context=context)
            else:
                add_registration_action(
                    session, wiz.event_id.id, partner_ids,
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
    p_obj = self.pool['res.partner']
    r_fields = ['email_coordinate_id', 'mobile_coordinate_id',
                'fix_coordinate_id']
    for p_value in p_obj.read(
            cr, uid, partner_ids, r_fields, context=context):
        vals['partner_id'] = p_value['id']
        # select mobile id or fix id of no phone
        phone_id = p_value['mobile_coordinate_id'] and \
            p_value['mobile_coordinate_id'][0] or \
            p_value['fix_coordinate_id'] and \
            p_value['fix_coordinate_id'][0] or False
        if phone_id:
            ph_obj = self.pool['phone.coordinate']
            vals['phone'] = ph_obj.browse(
                cr, uid, phone_id, context=context).phone_id.name
        email_id = p_value['email_coordinate_id'] and \
            p_value['email_coordinate_id'][0] or False
        if email_id:
            e_obj = self.pool['email.coordinate']
            vals['email'] = e_obj.read(
                cr, uid, email_id, ['email'],
                context=context)['email']
        reg_obj = self.pool['event.registration']
        reg_obj.create(cr, uid, vals, context=context)

    return
