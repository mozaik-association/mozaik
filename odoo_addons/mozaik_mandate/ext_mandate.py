# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields

from openerp.addons.mozaik_mandate.abstract_mandate import abstract_candidature
from openerp.addons.mozaik_mandate.mandate import mandate_category

CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('rejected', 'Rejected'),
    ('suggested', 'Suggested'),
    ('elected', 'Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)


class ext_selection_committee(orm.Model):
    _name = 'ext.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    _candidature_model = 'ext.candidature'
    _assembly_model = 'ext.assembly'
    _assembly_category_model = 'ext.assembly.category'
    _mandate_category_foreign_key = 'ext_assembly_category_id'
    _form_view = 'ext_selection_committee_form_view'
    _parameters_key = 'ext_candidature_invalidation_delay'

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        return super(ext_selection_committee,
                     self)._get_suggested_candidatures(cr,
                                                       uid,
                                                       ids,
                                                       context=context)

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category',
                                               string='Mandate Category',
                                               required=True,
                                               track_visibility='onchange',
                                               domain=[('type', '=', 'ext')]),
        'is_virtual': fields.boolean('Is Virtual'),
        'assembly_id': fields.many2one(_assembly_model,
                                       string='External Assembly',
                                       track_visibility='onchange'),
        'candidature_ids': fields.one2many(_candidature_model,
                                           'selection_committee_id',
                                           'External Candidatures',
                                           domain=[('active', '<=', True)],
                                           context={'force_recompute': True}),
        'assembly_category_id': fields.related(
            'mandate_category_id',
            _mandate_category_foreign_key,
            string='External Assembly Category',
            type='many2one',
            relation=_assembly_category_model,
            store=False),
        'partner_ids': fields.many2many(
            'res.partner', 'ext_selection_committee_res_partner_rel',
            'committee_id', 'partner_id',
            string='Members', domain=[('is_company', '=', False)]),
    }

    _defaults = {
        'is_virtual': True,
    }

    _order = 'assembly_id, mandate_start_date, mandate_category_id, name'

# constraints

    _unicity_keys = 'assembly_id, mandate_start_date, mandate_category_id, \
                    name'

# view methods: onchange, button

    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected external candidatures
        :rparam: True
        :rtype: boolean
        """
        return super(ext_selection_committee, self).action_copy(
            cr,
            uid,
            ids,
            context=context)

    def button_accept_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_accept_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in
        order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        return super(ext_selection_committee,
                     self).button_accept_candidatures(cr,
                                                      uid,
                                                      ids,
                                                      context=context)

    def button_refuse_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_refuse_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in
        order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        return super(ext_selection_committee,
                     self).button_refuse_candidatures(cr,
                                                      uid,
                                                      ids,
                                                      context=context)

    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        return super(ext_selection_committee,
                     self).onchange_assembly_id(cr,
                                                uid,
                                                ids,
                                                assembly_id,
                                                context=None)

    def process_invalidate_candidatures_after_delay(self, cr, uid,
                                                    context=None):
        """
        ===========================================
        process_invalidate_candidatures_after_delay
        ===========================================
        This method is used to invalidate candidatures after a defined
        elapsed time
        :rparam: True
        :rtype: boolean
        """
        return super(ext_selection_committee,
                     self).process_invalidate_candidatures_after_delay(
            cr,
            uid,
            context=context)


class ext_candidature(orm.Model):

    _name = 'ext.candidature'
    _description = "External Candidature"
    _inherit = ['abstract.candidature']

    _mandate_model = 'ext.mandate'
    _selection_committee_model = 'ext.selection.committee'
    _init_mandate_columns = list(abstract_candidature._init_mandate_columns)
    _init_mandate_columns.extend(['ext_assembly_id',
                                  'months_before_end_of_mandate'])
    _allowed_inactive_link_models = [_selection_committee_model]
    _mandate_form_view = 'ext_mandate_form_view'
    _unique_id_sequence = 400000000

    _mandate_category_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['mandate_category_id'], 20),
    }

    _ext_assembly_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['ext_assembly_id'], 20),
    }

    _designation_assembly_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['designation_int_assembly_id'], 20),
    }

    _mandate_start_date_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                     self.pool.get('ext.candidature').search(
                                         cr,
                                         uid,
                                         [('selection_committee_id',
                                           'in', ids)],
                                         context=context),
                                     ['mandate_start_date'], 20),
    }

    _columns = {
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES,
                                  'Status',
                                  readonly=True,
                                  track_visibility='onchange',),
        'selection_committee_id': fields.many2one(_selection_committee_model,
                                                  string='Selection Committee',
                                                  required=True,
                                                  select=True,
                                                  track_visibility='onchange'),
        'mandate_category_id': fields.related(
            'selection_committee_id',
            'mandate_category_id',
            string='Mandate Category',
            type='many2one',
            relation="mandate.category",
            store=_mandate_category_store_trigger,
            domain=[('type', '=', 'ext')]),
        'mandate_start_date': fields.related(
            'selection_committee_id',
            'mandate_start_date',
            string='Mandate Start Date',
            type='date',
            store=_mandate_start_date_store_trigger),
        'ext_assembly_id': fields.related('selection_committee_id',
                                          'assembly_id',
                                          string='External Assembly',
                                          type='many2one',
                                          relation="ext.assembly",
                                          store=_ext_assembly_store_trigger),
        'designation_int_assembly_id': fields.related(
            'selection_committee_id',
            'designation_int_assembly_id',
            string='Designation Assembly',
            type='many2one',
            relation="int.assembly",
            store=_designation_assembly_store_trigger),
        'months_before_end_of_mandate': fields.related(
            'ext_assembly_id',
            'months_before_end_of_mandate',
            string='Alert Delay (#Months)',
            type='integer',
            relation="ext.assembly",
            store=False),
        'mandate_ids': fields.one2many(_mandate_model,
                                       'candidature_id',
                                       'External Mandates',
                                       domain=[('active', '<=', True)]),
    }

    _order = 'ext_assembly_id, mandate_start_date, mandate_category_id, \
              partner_name'

# view methods: onchange, button

    def onchange_selection_committee_id(self, cr, uid, ids,
                                        selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get(
            self._selection_committee_model).browse(
            cr,
            uid,
            selection_committee_id,
            context)
        assembly = selection_committee.designation_int_assembly_id.id
        res['value'] = dict(
            ext_assembly_id=selection_committee.assembly_id.id,
            designation_int_assembly_id=assembly,
            mandate_category_id=selection_committee.mandate_category_id.id)
        return res

    def button_create_mandate(self, cr, uid, ids, context=None):
        return super(ext_candidature,
                     self).button_create_mandate(cr, uid, ids, context=context)


class ext_mandate(orm.Model):

    _name = 'ext.mandate'
    _description = "External Mandate"
    _inherit = ['abstract.mandate']

    _allowed_inactive_link_models = ['ext.candidature']
    _undo_redirect_action = 'mozaik_mandate.ext_mandate_action'
    _unique_id_sequence = 400000000

    _unique_id_store_trigger = {
        'ext.mandate': (lambda self, cr, uid, ids, context=None:
                        ids, ['partner_id'], 20),
    }

    def _compute_unique_id(self, cr, uid, ids, fname, arg, context=None):
        return super(ext_mandate,
                     self)._compute_unique_id(cr,
                                              uid,
                                              ids,
                                              fname,
                                              arg,
                                              context=context)

    _columns = {
        'unique_id': fields.function(_compute_unique_id,
                                     type="integer",
                                     string="Unique id",
                                     store=_unique_id_store_trigger),
        'mandate_category_id': fields.many2one('mandate.category',
                                               string='Mandate Category',
                                               select=True,
                                               required=True,
                                               track_visibility='onchange',
                                               domain=[('type', '=', 'ext')]),
        'ext_assembly_id': fields.many2one('ext.assembly',
                                           'External Assembly',
                                           select=True,
                                           required=True),
        'ext_assembly_category_id': fields.related(
            'mandate_category_id',
            'ext_assembly_category_id',
            string='External Assembly Category',
            type='many2one',
            relation="ext.assembly.category",
            store=False),
        'candidature_id': fields.many2one('ext.candidature',
                                          'Candidature'),
        'is_submission_mandate': fields.related(
            'mandate_category_id',
            'is_submission_mandate',
            string='With Wages Declaration',
            help='Submission to a Mandates and Wages Declaration',
            type='boolean',
            store={
                'mandate.category': (
                    mandate_category.get_linked_ext_mandate_ids,
                    ['is_submission_mandate'], 20)
            }),
        'is_submission_assets': fields.related(
            'mandate_category_id',
            'is_submission_assets',
            string='With Assets Declaration',
            help='Submission to a Mandates and Assets Declaration',
            type='boolean',
            store={
                'mandate.category': (
                    mandate_category.get_linked_ext_mandate_ids,
                    ['is_submission_assets'], 20)
            }),
        'competencies_m2m_ids': fields.many2many(
            'thesaurus.term',
            'ext_mandate_term_competencies_rel',
            id1='ext_mandate_id',
            id2='thesaurus_term_id',
            string='Remits'),
        'months_before_end_of_mandate': fields.integer(
            'Alert Delay (#Months)',
            track_visibility='onchange', group_operator='max'),
    }

    _order = 'partner_id, ext_assembly_id, start_date, mandate_category_id'

# constraints

    _unicity_keys = 'partner_id, ext_assembly_id, start_date, \
                     mandate_category_id'

# view methods: onchange, button

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id,
                                     context=None):
        ext_assembly_category_id = False

        if mandate_category_id:
            category_data = self.pool.get('mandate.category').read(
                cr,
                uid,
                mandate_category_id,
                ['ext_assembly_category_id'],
                context)
            ext_assembly_category_id =\
                category_data['ext_assembly_category_id'] or False

        res = {
            'ext_assembly_category_id': ext_assembly_category_id,
            'ext_assembly_id': False,
        }
        return {
            'value': res,
        }

    def onchange_ext_assembly_id(self, cr, uid, ids, ext_assembly_id,
                                 context=None):
        res = {}
        res['value'] = dict(months_before_end_of_mandate=False,
                            designation_int_assembly_id=False)
        if ext_assembly_id:
            assembly = self.pool.get('ext.assembly').browse(cr,
                                                            uid,
                                                            ext_assembly_id)

            months_before_end_of_mandate = \
                assembly.months_before_end_of_mandate
            designation_int_assembly_id = \
                assembly.designation_int_assembly_id.id
            res['value'] = dict(
                months_before_end_of_mandate=months_before_end_of_mandate,
                designation_int_assembly_id=designation_int_assembly_id)

        return res
