# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_address, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_address is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_address is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_address.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID

from openerp import fields as new_fields, api
from openerp.tools.translate import _


class change_main_address(orm.TransientModel):

    _name = 'change.main.address'
    _inherit = 'change.main.coordinate'
    _description = 'Change Main Address Wizard'

    _columns = {
        'old_address_id': fields.many2one(
            'address.address', 'Current Main Address'),
        'address_id': fields.many2one(
            'address.address', 'New Main Address',
            required=True, ondelete='cascade'),
    }

    co_residency_id = new_fields.Many2one('co.residency', 'Co-Residency')
    move_co_residency = new_fields.Boolean('Move Co-Residency', default=True)
    invalidate_co_residency = new_fields.Boolean('Invalidate Co-Residency',
                                                 default=True)
    move_allowed = new_fields.Boolean('Move Allowed')
    message = new_fields.Char('Message')

    def default_get(self, cr, uid, flds, context):
        context = dict(context)
        res = super(change_main_address, self).default_get(
            cr, uid, flds, context=context)
        if context.get('mode', False) == 'switch':
            coord = self.pool[context.get('target_model')].browse(
                cr, uid, context.get('target_id', False))
            res['address_id'] = coord.address_id.id
        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []
        if len(ids) == 1:
            partner = self.pool['res.partner'].browse(
                cr, SUPERUSER_ID, ids[0], context=context)
            res['old_address_id'] = partner.postal_coordinate_id.address_id.id
            if context.get('address_id', False):
                res['change_allowed'] = not(
                    res['address_id'] == res['old_address_id'])
            if res.get('old_address_id', False):
                cores_obj = self.pool.get('co.residency')
                cores_wiz_obj = self.pool.get('change.co.residency.address')
                co_res = cores_obj.search(
                    cr, uid, [('address_id', '=', res['old_address_id'])],
                    context=context)
                if co_res:
                    co_res_id = co_res[0]
                    if co_res_id:
                        res['move_allowed'] = cores_wiz_obj._use_allowed(
                            cr, uid, co_res_id, context=context)
                    res['co_residency_id'] = co_res_id
                    res['move_co_residency'] = res.get('move_allowed', False)
                    res['invalidate_co_residency'] = res.get('move_allowed',
                                                             False)
                    if not res.get('move_allowed', False):
                        res['message'] = _('Due to security restrictions'
                                           ' you are not allowed to move'
                                           ' all co-residency members !')
        return res

    @api.multi
    def button_change_main_coordinate(self):
        res = super(change_main_address,
                    self._model).button_change_main_coordinate(
            self.env.cr, self.env.uid, self.ids, self.env.context.copy())
        if self.co_residency_id and self.move_co_residency:
            cores_wiz_obj = self.env['change.co.residency.address']
            vals = {
                'co_residency_id': self.co_residency_id.id,
                'old_address_id': self.old_address_id.id,
                'address_id': self.address_id.id,
                'use_allowed': self.move_allowed,
                'invalidate': self.invalidate_co_residency,
            }
            wizard = cores_wiz_obj.create(vals)
            wizard.change_address()
        return res
