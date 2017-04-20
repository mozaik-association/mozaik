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

from openerp.osv import orm, fields


class change_main_address(orm.TransientModel):

    _inherit = 'change.main.address'

    _columns = {
        'keeping_mode': fields.integer(string='Mode'),
        # 1: mandatory
        # 2: user's choice
        # 3: forbiden
        'keep_instance': fields.boolean(
            string='Keep Previous Internal Instance?'),
        'old_int_instance_id': fields.many2one(
            'int.instance', string='Previous Internal Instance',
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

        ids = context.get('active_ids') or context.get('active_id') and \
            [context.get('active_id')] or []

        res['keeping_mode'] = 1
        res['keep_instance'] = False

        if len(ids) == 1:
            res['keeping_mode'] = 1
            for partner in self.pool['res.partner'].browse(cr, uid, ids,
                                                           context=context):
                if partner.int_instance_id:
                    res['keep_instance'] = partner.is_company
                    res['old_int_instance_id'] = partner.int_instance_id.id
            res['keeping_mode'] = 3

        return res

# view methods: onchange, button

    def onchange_address_id(self, cr, uid, ids, address_id,
                            old_int_instance_id, context=None):
        res = {}
        new_int_instance_id = False
        keeping_mode = 3
        if not old_int_instance_id:
            keeping_mode = 1
        elif address_id:
            adr = self.pool['address.address'].browse(cr, uid, address_id,
                                                      context=context)
            if adr.address_local_zip_id:
                new_int_instance_id = \
                    adr.address_local_zip_id.int_instance_id.id
            else:
                new_int_instance_id = self.pool['int.instance'].\
                    get_default(cr, uid, context=None)
            if old_int_instance_id != new_int_instance_id:
                keeping_mode = 2
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
