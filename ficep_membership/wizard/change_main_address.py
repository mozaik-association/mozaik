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

from openerp.osv import orm, fields


class change_main_address(orm.TransientModel):

    _inherit = 'change.main.address'

    _columns = {
        'keeping_mode': fields.integer(string='Mode'),
        # 1: mandatory
        # 2: user's choice
        # 3: forbiden
        'keep_instance': fields.boolean(
            string='Keep Current Internal Instance?'),
        'old_int_instance_id': fields.many2one(
            'int.instance', string='Current Internal Instance',
            ondelete='cascade'),
        'new_int_instance_id': fields.many2one(
            'int.instance', string='New Internal Instance',
            ondelete='cascade'),
    }

    def default_get(self, cr, uid, fields, context):
        """
        To get default values for the object.
        """
        res = super(change_main_address, self).default_get(cr, uid, fields,
                                                           context=context)
        context = context or {}

        ids = context.get('active_id') and [context.get('active_id')] or \
            context.get('active_ids') or []
        if ids:
            for partner in self.pool['res.partner'].browse(cr, uid, ids,
                                                           context=context):
                if partner.int_instance_id:
                    res['keep_instance'] = partner.is_company
                    res['old_int_instance_id'] = partner.int_instance_id.id
                else:
                    res['keep_instance'] = False
                break
            res['keeping_mode'] = 3

        return res

# view methods: onchange, button

    def onchange_address_id(self, cr, uid, ids, address_id,
                            old_int_instance_id, context=None):
        res = {}
        new_int_instance_id = False
        keeping_mode = 3
        if address_id:
            adr = self.pool['address.address'].browse(cr, uid, address_id,
                                                      context=context)
            if adr.address_local_zip_id:
                new_int_instance_id = \
                    adr.address_local_zip_id.int_instance_id.id
            else:
                new_int_instance_id = self.pool['int.instance'].\
                    get_default(cr, uid, context=None)
            keeping_mode = not old_int_instance_id and 1 or \
                old_int_instance_id != new_int_instance_id and 2 or 3
        res.update({'new_int_instance_id': new_int_instance_id,
                    'keeping_mode': keeping_mode})
        return {'value': res}

# public methods

    def button_change_main_coordinate(self, cr, uid, ids, context=None):
        """
        Change main coordinate for a list of partners
        * a new main coordinate is created for each partner
        * the previsous main coordinate is invalidates or not regarding
          the option ``invalidate_previous_coordinate``
        :raise: ERROR if no partner selected

        **Note**
        When launched from the partner form the partner id is taken ``res_id``
        """
        context = context or {}

        wizard = self.browse(cr, uid, ids, context=context)[0]
        if wizard.keeping_mode == 2 and wizard.keep_instance:
            context.update({'keep_current_instance': True})

        return super(change_main_address, self).button_change_main_coordinate(
            cr, uid, ids, context=context)
