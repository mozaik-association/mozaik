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
from openerp.tools.translate import _
from .abstract_mandate import abstract_candidature
from .abstract_mandate import create_mandate_from_candidature
from .mandate import mandate_category


class sta_candidature(orm.Model):

    _name = 'sta.candidature'
    _description = "State Candidature"
    _inherit = ['abstract.candidature']

    _mandate_model = 'sta.mandate'
    _init_mandate_columns = abstract_candidature._init_mandate_columns
    _init_mandate_columns.extend(['legislature_id', 'sta_assembly_id'])
    _allowed_inactive_link_models = ['selection.committee']

    _columns = {
        'electoral_district_id': fields.related('selection_committee_id', 'electoral_district_id', string='Electoral District',
                                          type='many2one', relation="electoral.district",
                                          store=True),
        'legislature_id': fields.related('selection_committee_id', 'legislature_id', string='Legislature',
                                          type='many2one', relation="legislature",
                                          store=True),
        'sta_assembly_id': fields.related('selection_committee_id', 'sta_assembly_id', string='State Assembly',
                                          type='many2one', relation="sta.assembly",
                                          store=True),
        'is_effective': fields.boolean('Effective', track_visibility='onchange'),
        'is_substitute': fields.boolean('Substitute', track_visibility='onchange'),
        'list_effective_position': fields.integer('Position on effectives list', track_visibility='onchange'),
        'list_substitute_position': fields.integer('Position on substitutes list', track_visibility='onchange'),
        'election_effective_position': fields.integer('Effective position after election', track_visibility='onchange'),
        'election_substitute_position': fields.integer('Substitute position after election', track_visibility='onchange'),
        'effective_votes': fields.integer('Effective preferential votes', track_visibility='onchange'),
        'substitute_votes': fields.integer('Substitute preferential votes', track_visibility='onchange'),
        'is_legislative': fields.related('sta_assembly_id', 'is_legislative', string='Is Legislative',
                                          type='boolean', relation="sta.assembly",
                                          store=True),
        }

    # view methods: onchange, button
    def onchange_selection_committee_id(self, cr, uid, ids, selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get('selection.committee').browse(cr, uid, selection_committee_id, context)

        res['value'] = dict(legislature_id=selection_committee.legislature_id.id or False,
                            electoral_district_id=selection_committee.electoral_district_id.id or False,
                            sta_assembly_id=selection_committee.sta_assembly_id.id or False,
                            designation_int_assembly_id=selection_committee.designation_int_assembly_id.id or False,
                            mandate_category_id=selection_committee.mandate_category_id.id or False,
                            is_legislative=selection_committee.sta_assembly_id.is_legislative or False,)
        return res

    def action_elected(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'elected'})
        for candidature in self.browse(cr, uid, ids, context):
            if candidature.selection_committee_id.auto_mandate:
                create_mandate_from_candidature(cr, uid, self, candidature.id, context)
        return True

    def button_create_mandate(self, cr, uid, ids, context=None):
        for candidature_id in ids:
            mandate_id = create_mandate_from_candidature(cr, uid, self, candidature_id, context)

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_mandate', 'sta_mandate_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mandate'),
            'res_model': 'sta.mandate',
            'res_id': mandate_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }


class sta_mandate(orm.Model):
    _name = 'sta.mandate'
    _description = "State Mandate"
    _inherit = ['abstract.mandate']

    _columns = {
        'legislature_id': fields.many2one('legislature', string='Legislature',
                                                 required=True, track_visibility='onchange'),
        'sta_assembly_id': fields.many2one('sta.assembly', string='State Assembly'),
        'sta_assembly_category_id': fields.related('mandate_category_id', 'sta_assembly_category_id', string='State Assembly Category',
                                          type='many2one', relation="sta.assembly.category",
                                          store=False),
        'candidature_id': fields.many2one('sta.candidature', 'Candidature'),
        'is_submission_mandate': fields.related('mandate_category_id', 'is_submission_mandate', string='Submission to a mandate declaration',
                                          type='boolean', relation="mandate.category",
                                          store={'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['is_submission_mandate'], 20)}),
        'is_submission_assets': fields.related('mandate_category_id', 'is_submission_assets', string='Submission to an assets declaration',
                                          type='boolean', relation="mandate.category",
                                          store={'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['is_submission_assets'], 20)}),
        'is_legislative': fields.related('sta_assembly_id', 'is_legislative', string='Is Legislative',
                                          type='boolean', relation="sta.assembly",
                                          store=True),
        'competencies_m2m_ids': fields.many2many('thesaurus.term', 'sta_mandate_term_competencies_rel', id1='sta_mandate_id', id2='thesaurus_term_id', string='Competencies'),
        }

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_invalidate
        =================
        Invalidates an object
        :rparam: True
        :rtype: boolean
        Note: Argument vals must be the last in the signature
        """
        return super(sta_mandate, self).action_invalidate(cr, uid, ids, context=context, vals=vals)

    def action_finish(self, cr, uid, ids, context=None):
        """
        =================
        action_finish
        =================
        Finish mandate at the current date
        :rparam: True
        :rtype: boolean
        """
        return super(sta_mandate, self).action_finish(cr, uid, ids, context=context)
