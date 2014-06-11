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

INVOICE_AVAILABLE_TYPES = [
    ('month', 'Monthly'),
    ('year', 'Yearly'),
    ('none', 'None'),
]


class mandate_category(orm.Model):

    _name = 'mandate.category'
    _description = 'Mandate Category'
    _inherit = ['mandate.category']

    _columns = {
        'fractionation_id': fields.many2one('fractionation', string='Fractionation', track_visibility='onchange'),
        'calculation_method_id': fields.many2one('calculation.method', string='Calculation method', track_visibility='onchange'),
        'invoice_type': fields.selection(INVOICE_AVAILABLE_TYPES, 'Invoicing', required=True)
    }

    _defaults = {
        'invoice_type': INVOICE_AVAILABLE_TYPES[2][0]
    }
