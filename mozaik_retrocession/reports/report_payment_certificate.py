# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_retrocession, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_retrocession is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_retrocession is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_retrocession.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.report import report_sxw


class report_payment_certificate(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_payment_certificate, self).__init__(cr, uid, name,
                                                         context=context)
        self.localcontext.update({
            'modulo': self._modulo,
        })

    def _modulo(self, number, modulo):
        return number % modulo


class report_payment_certificate_wrapper(osv.AbstractModel):
    _name = 'report.mozaik_retrocession.report_payment_certificate'
    _inherit = 'report.abstract_report'
    _template = 'mozaik_retrocession.report_payment_certificate'
    _wrapped_report_class = report_payment_certificate
