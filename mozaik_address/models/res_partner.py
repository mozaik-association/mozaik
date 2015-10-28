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

from openerp import models
from openerp.tools.translate import _
import base64


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def get_print_coordinate_actions(self, cr, uid, context=None):
        context = context or {}
        context['active_model'] = 'postal.coordinate'
        partner_ids = context.get('active_ids')
        domain = [
            ('is_main', '=', True),
            ('partner_id', 'in', partner_ids),
        ]
        postal_ids = self.pool['postal.coordinate'].search(
            cr, uid, domain, context=context)
        context['active_ids'] = postal_ids
        report = self.pool['ir.actions.report.xml'].render_report(
            cr, uid, postal_ids,
            'mozaik_address.report_postal_coordinate_label',
            {'report_type': 'qweb-pdf'}, context=context)
        if report:
            pdf = base64.encodestring(report[0])
            context['default_export_file'] = pdf
            context['default_export_filename'] = 'postal_labels.pdf'
            return {
                'name': _('Print Postal Labels from Partners'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.postal.from.partner.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': context,
             }
