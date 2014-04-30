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

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _

#===============================================================================
# from .abstract_mandate import abstract_candidature
# from .abstract_mandate import create_mandate_from_candidature
# from .mandate import mandate_category
#===============================================================================


class ext_selection_committee(orm.Model):
    _name = 'ext.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    def _get_suggested_ext_candidatures(self, ext_candidature_ids):
        res = []
        for candidature in ext_candidature_ids:
            if candidature.state == 'rejected':
                continue
            elif candidature.state == 'suggested':
                res.append(candidature.id)
            else:
                raise osv.except_osv(_('Operation Forbidden!'),
                             _('All candidatures are not in suggested state'))
        return res

    _columns = {
        'is_virtual': fields.boolean('Is Virtual'),
        'ext_assembly_id': fields.many2one('ext.assembly', string='External Assembly', track_visibility='onchange'),
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange', domain=[('type', '=', 'ext')]),
        'ext_assembly_category_id': fields.related('mandate_category_id', 'ext_assembly_category_id', string='External Assembly Category',
                                          type='many2one', relation="ext.assembly.category",
                                          store=False),
    }

    _defaults = {
        'is_virtual': False,
    }

# constraints

    _unicity_keys = 'N/A'