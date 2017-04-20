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

from openerp.osv import osv
from openerp.report import report_sxw


class report_postal_coordinate_label(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_postal_coordinate_label, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'modulo': self._modulo,
            'co': context.get('groupby_co_residency'),
        })

    def _modulo(self, number, modulo):
        return number % modulo


class report_postal_coordinate_label_wrapper(osv.AbstractModel):
    _name = 'report.mozaik_address.report_postal_coordinate_label'
    _inherit = 'report.abstract_report'
    _template = 'mozaik_address.report_postal_coordinate_label'
    _wrapped_report_class = report_postal_coordinate_label
