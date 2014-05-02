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

from .abstract_mandate import abstract_candidature
#===============================================================================
# from .abstract_mandate import create_mandate_from_candidature
# from .mandate import mandate_category
#===============================================================================
CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('rejected', 'Rejected'),
    ('suggested', 'Suggested'),
    ('elected', 'Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)


class int_selection_committee(orm.Model):
    _name = 'int.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    def _get_suggested_int_candidatures(self, int_candidature_ids):
        res = []
        for candidature in int_candidature_ids:
            if candidature.state == 'rejected':
                continue
            elif candidature.state == 'suggested':
                res.append(candidature.id)
            else:
                raise osv.except_osv(_('Operation Forbidden!'),
                             _('All candidatures are not in suggested state'))
        return res

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                         required=True, track_visibility='onchange', domain=[('type', '=', 'int')]),
        'is_virtual': fields.boolean('Is Virtual'),
        'int_assembly_id': fields.many2one('int.assembly', string='Internal Assembly', track_visibility='onchange'),
        'int_assembly_category_id': fields.related('mandate_category_id', 'int_assembly_category_id', string='Internal Assembly Category',
                                          type='many2one', relation="int.assembly.category",
                                          store=False),
        'int_candidature_ids': fields.one2many('int.candidature', 'selection_committee_id', 'Internal Candidatures',
                                               domain=[('active', '<=', True)]),
    }

    _defaults = {
        'is_virtual': False,
    }

# constraints

    _unicity_keys = 'N/A'

    # view methods: onchange, button
    def onchange_int_assembly_id(self, cr, uid, ids, int_assembly_id, context=None):
        res = {}
        res['value'] = dict(designation_int_assembly_id=False)
        if int_assembly_id:
            assembly_data = self.pool.get('int.assembly').read(cr, uid, int_assembly_id, ['designation_int_assembly_id'])
            res['value'] = dict(designation_int_assembly_id=assembly_data['designation_int_assembly_id'] or False)
        return res


class int_candidature(orm.Model):

    _name = 'int.candidature'
    _description = "Internal Candidature"
    _inherit = ['abstract.candidature']

    _mandate_model = 'int.mandate'
    _selection_committee_model = 'int.selection.committee'
    _init_mandate_columns = abstract_candidature._init_mandate_columns
    _init_mandate_columns.extend(['int_assembly_id'])
    _allowed_inactive_link_models = [_selection_committee_model]

    _columns = {
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one(_selection_committee_model, string='Selection Committee',
                                                 required=True, select=True, track_visibility='onchange'),
        'mandate_category_id': fields.related('selection_committee_id', 'mandate_category_id', string='Mandate Category',
                                          type='many2one', relation="mandate.category",
                                          store=True, domain=[('type', '=', 'int')]),
        'int_assembly_id': fields.related('selection_committee_id', 'int_assembly_id', string='Internal Assembly',
                                          type='many2one', relation="int.assembly",
                                          store=True),
    }

    _order = 'selection_committee_id'

    # view methods: onchange, button
    def onchange_selection_committee_id(self, cr, uid, ids, selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get(self._selection_committee_model).browse(cr, uid, selection_committee_id, context)

        res['value'] = dict(int_assembly_id=selection_committee.int_assembly_id.id or False,
                            designation_int_assembly_id=selection_committee.designation_int_assembly_id.id or False,
                            mandate_category_id=selection_committee.mandate_category_id.id or False,)
        return res
