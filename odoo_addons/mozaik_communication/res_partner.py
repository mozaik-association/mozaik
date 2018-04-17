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
from openerp import SUPERUSER_ID, api, models, fields


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner']

    opt_out_ids = fields.Many2many(
        comodel_name='distribution.list',
        relation='distribution_list_res_partner_out',
        column1='partner_id',
        column2='distribution_list_id',
        string='Opt-Out',
        domain=[('newsletter', '=', True)])
    opt_in_ids = fields.Many2many(comodel_name='distribution.list',
                                  relation='distribution_list_res_partner_in',
                                  column1='partner_id',
                                  column2='distribution_list_id',
                                  string='Opt-In',
                                  domain=[('newsletter', '=', True)])
    responsible_user_id = fields.Many2one(
        comodel_name='res.users', string='Responsible User', index=True)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """
        Bypass security for some fields
        """
        if self.env.user.id != SUPERUSER_ID:
            flds = set(fields or self._fields) - set([
                '__last_update', 'image_medium', 'image_small',
            ])
            if not flds:
                return super(ResPartner, self.sudo()).read(
                    fields=fields, load=load)
        return super(ResPartner, self).read(fields=fields, load=load)
