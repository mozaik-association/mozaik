# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_phone, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_phone is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_phone is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_phone.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, exceptions
from openerp.addons.mozaik_phone import phone_phone
from openerp.tools.translate import _


class ChangePhoneType(models.TransientModel):
    _name = 'change.phone.type'
    _description = "Change Phone Type Wizard"

    phone_id = fields.Many2one(string='Phone',
                               comodel_name="phone.phone")
    is_main = fields.Boolean('Set as main', default=True)
    type = fields.Selection(string='Type',
                            selection=phone_phone.PHONE_AVAILABLE_TYPES)

    @api.model
    def default_get(self, fields_lists):
        res = super(ChangePhoneType, self).default_get(fields_lists)
        model = self.env.context.get('active_model', False)
        if not model:
            return res

        ids = self.env.context.get('active_ids') \
            or (self.env.context.get('active_id')
                and [self.env.context.get('active_id')]) \
            or []
        phone = self.env[model].browse(ids[0])
        res['phone_id'] = phone.id
        return res

    @api.multi
    def change_phone_type(self):
        if self.type == self.phone_id.type:
            raise exceptions.Warning(_('New phone type should be different'
                                       ' than current one!'))

        self.phone_id.phone_coordinate_ids.ensure_one_main_coordinate(
            invalidate=False)
        self.phone_id.write({'type': self.type})
        if not self.is_main:
            self.phone_id.phone_coordinate_ids.write({'is_main': False})

        for coordinate in self.phone_id.phone_coordinate_ids:
            if self.is_main:
                wiz_obj = self.env['change.main.phone']
                context = dict(active_model='phone.coordinate',
                               target_model='phone.coordinate',
                               mode='switch',
                               active_id=coordinate.id)
                wiz_id = wiz_obj._model.create(
                    self.env.cr, self.env.uid, {}, context=context)
                wiz_obj._model.button_change_main_coordinate(
                    self.env.cr, self.env.uid, wiz_id, context=context)
        return True
