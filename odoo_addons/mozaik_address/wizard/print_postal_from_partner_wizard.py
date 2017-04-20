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

from openerp import models, api


class PrintPostalFromPartnerWizard(models.TransientModel):

    _name = 'print.postal.from.partner.wizard'
    _description = 'Print Postal From Partner Wizard'

    @api.multi
    def print_postal_from_partner_button(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx['active_model'] = 'postal.coordinate'
        partner_ids = ctx.get('active_ids')
        domain = [
            ('is_main', '=', True),
            ('partner_id', 'in', partner_ids),
        ]
        postal_ids = self.env['postal.coordinate'].search(domain)
        ctx['active_ids'] = postal_ids.ids
        return self.pool['report'].get_action(
            self.env.cr, self.env.uid, [],
            'mozaik_address.report_postal_coordinate_label',
            data={'report_type': 'qweb-pdf'}, context=ctx)
