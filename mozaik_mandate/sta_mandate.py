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
from openerp.tools import SUPERUSER_ID

from openerp.addons.mozaik_mandate.abstract_mandate import abstract_candidature
from openerp.addons.mozaik_mandate.mandate import mandate_category

CANDIDATURE_AVAILABLE_SORT_ORDERS = {
    'elected': 0,
    'non-elected': 10,
    'designated': 20,
    'suggested': 22,
    'declared': 24,
    'rejected': 30,
    'draft': 90,
}


class sta_selection_committee(orm.Model):
    _name = 'sta.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    _candidature_model = 'sta.candidature'
    _assembly_model = 'sta.assembly'
    _assembly_category_model = 'sta.assembly.category'
    _mandate_category_foreign_key = 'sta_assembly_category_id'
    _form_view = 'sta_selection_committee_form_view'
    _parameters_key = 'sta_candidature_invalidation_delay'

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        return super(sta_selection_committee,
                     self)._get_suggested_candidatures(cr,
                                                       uid,
                                                       ids,
                                                       context=context)

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category',
                                               string='Mandate Category',
                                               required=True,
                                               track_visibility='onchange',
                                               domain=[('type', '=', 'sta')]),
        'assembly_id': fields.many2one(_assembly_model,
                                       string='State Assembly',
                                       track_visibility='onchange'),
        'candidature_ids': fields.one2many(_candidature_model,
                                           'selection_committee_id',
                                           'State Candidatures',
                                           domain=[('active', '<=', True)]),
        'assembly_category_id': fields.related('mandate_category_id',
                                            _mandate_category_foreign_key,
                                            string='State Assembly Category',
                                            type='many2one',
                                            relation=_assembly_category_model,
                                            store=False),
        'electoral_district_id': fields.many2one('electoral.district',
                                                 string='Electoral District',
                                                 track_visibility='onchange'),
        'legislature_id': fields.many2one('legislature',
                                          string='Legislature',
                                          track_visibility='onchange'),
        'listname': fields.char('Name',
                                size=128,
                                track_visibility='onchange'),
        'is_cartel': fields.boolean('Is Cartel'),
        'cartel_composition': fields.text('Cartel composition',
                                          track_visibility='onchange'),
        'partner_ids': fields.many2many(
            'res.partner', 'sta_selection_committee_res_partner_rel',
            'committee_id', 'partner_id',
            string='Members', domain=[('is_company', '=', False)]),
    }

    _order = 'assembly_id, electoral_district_id, legislature_id,\
             mandate_category_id, name'

# constraints

    _unicity_keys = 'assembly_id, electoral_district_id, legislature_id,\
                    mandate_category_id, name'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if not context:
            context = self.pool.get('res.users').context_get(cr, uid)

        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for committee in self.browse(cr, uid, ids, context=context):
            display_name = u'{assembly}/{start} ({name})'.format(
                                assembly=committee.electoral_district_id.name\
                                         or committee.assembly_id.name,
                                start=self.pool.get('res.lang').format_date(
                                        cr,
                                        uid,
                                        committee.mandate_start_date,
                                        context) or False,
                                name=committee.name,)
            res.append((committee['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            assembly_ids = self.pool['sta.assembly.category'].search(
                                                 cr,
                                                 uid,
                                                 [('name', operator, name)],
                                                 context=context)
            district_ids = self.pool['electoral.district'].search(
                                                 cr,
                                                 uid,
                                                 [('name', operator, name)],
                                                 context=context)
            ids = self.search(cr, uid, ['|',
                                        '|', ('name', operator, name),
                                             ('electoral_district_id',
                                              'in',
                                              district_ids),
                                        '&', ('assembly_id',
                                              'in',
                                              assembly_ids),
                                             ('electoral_district_id',
                                              '=',
                                              False)] + args,
                                    limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def copy_data(self, cr, uid, id_, default=None, context=None):
        default = default or {}

        res = super(sta_selection_committee, self).copy_data(cr, uid, id_,
                                                             default=default,
                                                             context=context)

        data = self.onchange_assembly_id(cr, uid, id_, res.get('assembly_id'),
                                         context=context)
        legislature_id = data['value']['legislature_id']
        legislature_data = self.onchange_legislature_id(cr, uid, id_,
                                                        legislature_id,
                                                        context=context)

        res.update({
            'legislature_id': legislature_id,
            'mandate_start_date': legislature_data['value'][\
                                                  'mandate_start_date'],
            'mandate_deadline_date': legislature_data['value'][\
                                                  'mandate_deadline_date'],
        })
        return res

# view methods: onchange, button

    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected state candidatures
        :rparam: True
        :rtype: boolean
        """
        return super(sta_selection_committee, self).action_copy(cr, uid, ids,
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
        return super(sta_selection_committee,
                     self).button_accept_candidatures(cr, uid, ids,
                                                      context=context)

    def button_refuse_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_refuse_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id
        in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        return super(sta_selection_committee,
                     self).button_refuse_candidatures(cr, uid, ids,
                                                      context=context)

    def onchange_electoral_district_id(self, cr, uid, ids,
                                       electoral_district_id, context=None):
        res = {}
        res['value'] = dict(assembly_id=False,
                            assembly_category_id=False,
                            designation_int_assembly_id=False)
        if electoral_district_id:
            district_data = self.pool.get('electoral.district').read(
                                             cr,
                                             uid,
                                             electoral_district_id,
                                             ['assembly_id',
                                              'designation_int_assembly_id'])
            res['value'] = dict(assembly_id=district_data['assembly_id']\
                                            or False,
                                designation_int_assembly_id=district_data[\
                                                 'designation_int_assembly_id']
                                                  or False)
        return res

    def onchange_legislature_id(self, cr, uid, ids, legislature_id,
                                context=None):
        res = {}
        res['value'] = dict(mandate_start_date=False,
                                mandate_deadline_date=False)
        if legislature_id:
            legislature_data = self.pool.get('legislature').read(
                                                    cr,
                                                    uid,
                                                    legislature_id,
                                                    ['start_date',
                                                     'deadline_date'])
            res['value'] = dict(mandate_start_date=legislature_data[\
                                                            'start_date'],
                                mandate_deadline_date=legislature_data[\
                                                            'deadline_date']
                                )
        return res

    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        res = super(sta_selection_committee,
                    self).onchange_assembly_id(cr, uid, ids,
                                               assembly_id, context=None)
        if assembly_id:
            assembly = self.pool.get(self._assembly_model).browse(cr, uid,
                                                                  assembly_id)
            legislature_ids = self.pool.get('legislature').search(cr, uid,
                            [('power_level_id',
                              '=',
                              assembly.assembly_category_id.power_level_id.id),
                             ('start_date', '>', fields.datetime.now())
                            ])
            legislature_id = False
            if legislature_ids:
                legislature_id = legislature_ids[0]

            res['value']['legislature_id'] = legislature_id
        return res

    def process_invalidate_candidatures_after_delay(self, cr, uid,
                                                    context=None):
        """
        ===========================================
        process_invalidate_candidatures_after_delay
        ===========================================
        This method is used to invalidate candidatures after a defined elapsed
        time
        :rparam: True
        :rtype: boolean
        """
        return super(sta_selection_committee,
                     self).process_invalidate_candidatures_after_delay(
                                                            cr,
                                                            uid,
                                                            context=context)


class sta_candidature(orm.Model):

    _name = 'sta.candidature'
    _description = 'State Candidature'
    _inherit = ['abstract.candidature']

    _mandate_model = 'sta.mandate'
    _selection_committee_model = 'sta.selection.committee'
    _init_mandate_columns = list(abstract_candidature._init_mandate_columns)
    _init_mandate_columns.extend(['legislature_id', 'sta_assembly_id'])
    _allowed_inactive_link_models = [_selection_committee_model]
    _mandate_form_view = 'sta_mandate_form_view'
    _unique_id_sequence = 200000000

# private methods

    def _get_sort_order(self, cr, uid, ids, name, args, context=None):
        """
        ===============
        _get_sort_order
        ===============
        Recompute sort order field
        :param ids: candidatures ids
        :type ids: list
        :rparam: dictionary for all partner ids with requested computed fields
        :rtype: dict {partner_id: sort_order}
        Note:
        Calling and result convention: Single mode
        """
        result = {i: False for i in ids}
        for cand in self.browse(cr, uid, ids, context=context):
            sort_order = CANDIDATURE_AVAILABLE_SORT_ORDERS.get(cand.state, 99)
            if cand.state == 'non-elected':
                if cand.is_effective and not cand.is_substitute:
                    sort_order += 1
            elif not cand.is_effective and cand.is_substitute:
                sort_order += 1
            result[cand.id] = sort_order
        return result

    _sort_order_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None: ids,
                           ['state', 'is_effective', 'is_substitute', ], 20)
    }

    _mandate_category_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                    self.pool.get('sta.candidature').search(
                                                    cr,
                                                    uid,
                                                    [('selection_committee_id',
                                                      'in',
                                                      ids)
                                                    ], context=context),
                                    ['mandate_category_id'], 20),
    }

    _electoral_district_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                    self.pool.get('sta.candidature').search(
                                                    cr,
                                                    uid,
                                                    [('selection_committee_id',
                                                      'in',
                                                      ids)
                                                    ], context=context),
                                    ['electoral_district_id'], 20),
    }

    _legislature_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                    self.pool.get('sta.candidature').search(
                                                    cr,
                                                    uid,
                                                    [('selection_committee_id',
                                                      'in',
                                                      ids)
                                                    ], context=context),
                                    ['legislature_id'], 20),
    }

    _sta_assembly_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                    self.pool.get('sta.candidature').search(
                                                    cr,
                                                    uid,
                                                    [('selection_committee_id',
                                                      'in',
                                                      ids)
                                                    ], context=context),
                                    ['sta_assembly_id'], 20),
    }

    _designation_assembly_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                    self.pool.get('sta.candidature').search(
                                                    cr,
                                                    uid,
                                                    [('selection_committee_id',
                                                      'in',
                                                      ids)
                                                    ], context=context),
                                    ['designation_int_assembly_id'], 20),
    }

    _mandate_start_date_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None:
                            ids, ['selection_committee_id'], 20),
        _selection_committee_model: (lambda self, cr, uid, ids, context=None:
                                    self.pool.get('sta.candidature').search(
                                                    cr,
                                                    uid,
                                                    [('selection_committee_id',
                                                      'in',
                                                      ids)
                                                    ], context=context),
                                    ['mandate_start_date'], 20),
    }

    _columns = {
        'selection_committee_id': fields.many2one(
                                    _selection_committee_model,
                                    string='Selection Committee',
                                    required=True,
                                    select=True,
                                    track_visibility='onchange'),
        'mandate_start_date': fields.related(
                                    'selection_committee_id',
                                    'mandate_start_date',
                                    string='Mandate Start Date',
                                    type='date',
                                    store=_mandate_start_date_store_trigger),
        'mandate_category_id': fields.related(
                                    'selection_committee_id',
                                    'mandate_category_id',
                                    string='Mandate Category',
                                    type='many2one',
                                    relation="mandate.category",
                                    store=_mandate_category_store_trigger,
                                    domain=[('type', '=', 'sta')]),
        'designation_int_assembly_id': fields.related(
                                    'selection_committee_id',
                                    'designation_int_assembly_id',
                                    string='Designation Assembly',
                                    type='many2one',
                                    relation="int.assembly",
                                    store=_designation_assembly_store_trigger),
        'sort_order': fields.function(
                                    _get_sort_order,
                                    type='integer',
                                    string='Sort Order',
                                    store=_sort_order_store_trigger),
        'electoral_district_id': fields.related(
                                    'selection_committee_id',
                                    'electoral_district_id',
                                    string='Electoral District',
                                    type='many2one',
                                    relation="electoral.district",
                                    store=_electoral_district_store_trigger),
        'legislature_id': fields.related(
                                    'selection_committee_id',
                                    'legislature_id',
                                    string='Legislature',
                                    type='many2one',
                                    relation="legislature",
                                    store=_legislature_store_trigger),
        'sta_assembly_id': fields.related(
                                    'selection_committee_id',
                                    'assembly_id',
                                    string='State Assembly',
                                    type='many2one',
                                    relation="sta.assembly",
                                    store=_sta_assembly_store_trigger),
        'is_effective': fields.boolean(
                                    'Effective',
                                    track_visibility='onchange'),
        'is_substitute': fields.boolean(
                                    'Substitute',
                                    track_visibility='onchange'),
        'list_effective_position': fields.integer(
                                    'Position on Effectives List',
                                    group_operator='max',
                                    track_visibility='onchange'),
        'list_substitute_position': fields.integer(
                                    'Position on Substitutes List',
                                    group_operator='max',
                                    track_visibility='onchange'),
        'election_effective_position': fields.integer(
                                    'Effective Position after Election',
                                    group_operator='max',
                                    track_visibility='onchange'),
        'election_substitute_position': fields.integer(
                                    'Substitute Position after Election',
                                    group_operator='max',
                                    track_visibility='onchange'),
        'effective_votes': fields.integer(
                                    'Effective Preferential Votes',
                                    track_visibility='onchange'),
        'substitute_votes': fields.integer(
                                    'Substitute Preferential Votes',
                                    track_visibility='onchange'),
        'is_legislative': fields.related(
                                    'sta_assembly_id',
                                    'is_legislative',
                                    string='Is Legislative',
                                    type='boolean',
                                    store=False),
        'mandate_ids': fields.one2many(
                                    _mandate_model,
                                    'candidature_id',
                                    'State Mandates',
                                    domain=[('active', '<=', True)]),
    }

    _defaults = {
        'list_effective_position': 0,
        'list_substitute_position': 0,
        'election_effective_position': 0,
        'election_substitute_position': 0,
        'effective_votes': 0,
        'substitute_votes': 0,
    }

    _order = 'sta_assembly_id, electoral_district_id, legislature_id,\
              mandate_category_id, sort_order, election_effective_position,\
              election_substitute_position, list_effective_position,\
              list_substitute_position, partner_name'

# constraints

    def _check_partner(self, cr, uid, ids, for_unlink=False, context=None):
        """
        ==============
        _check_partner
        ==============
        Check if partner doesn't have several candidatures in the same category
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        uid = SUPERUSER_ID
        candidatures = self.browse(cr, uid, ids)
        for candidature in candidatures:
            if len(self.search(cr, uid, [('partner_id',
                                          '=',
                                          candidature.partner_id.id),
                                         ('id', '!=', candidature.id),
                                         ('mandate_category_id',
                                          '=',
                                          candidature.mandate_category_id.id)
                                        ], context=context)) > 0:
                return False

        return True

    _constraints = [
        (_check_partner,
         _("A candidature already exists for this partner in this category"),
         ['partner_id'])
    ]

# view methods: onchange, button

    def onchange_selection_committee_id(self, cr, uid, ids,
                                        selection_committee_id, context=None):
        res = {}
        selection_committee = False
        if selection_committee_id:
            selection_committee =\
            self.pool.get(self._selection_committee_model).browse(
                                                      cr,
                                                      uid,
                                                      selection_committee_id,
                                                      context)

        res['value'] = dict(
                    legislature_id=selection_committee\
                      and selection_committee.legislature_id.id\
                      or False,
                    electoral_district_id=selection_committee\
                      and selection_committee.electoral_district_id.id\
                      or False,
                    sta_assembly_id=selection_committee
                      and selection_committee.assembly_id.id\
                      or False,
                    designation_int_assembly_id=selection_committee
                      and selection_committee.designation_int_assembly_id.id\
                      or False,
                    mandate_category_id=selection_committee\
                      and selection_committee.mandate_category_id.id\
                      or False,
                    is_legislative=selection_committee\
                      and selection_committee.assembly_id.is_legislative\
                      or False,)
        return res

    def onchange_effective_substitute(self, cr, uid, ids, is_effective,
                                      is_substitute, context=None):
        res = {}
        if not is_effective and is_substitute:
            res.update(list_effective_position=False)
        if not is_substitute:
            res.update(list_substitute_position=False)
        return {
            'value': res,
        }

    def button_create_mandate(self, cr, uid, ids, context=None):
        return super(sta_candidature, self).button_create_mandate(
                                                              cr,
                                                              uid,
                                                              ids,
                                                              context=context)


class sta_mandate(orm.Model):

    _name = 'sta.mandate'
    _description = "State Mandate"
    _inherit = ['abstract.mandate']

    _allowed_inactive_link_models = ['sta.candidature']
    _undo_redirect_action = 'mozaik_mandate.sta_mandate_action'
    _unique_id_sequence = 200000000

    _unique_id_store_trigger = {
            'sta.mandate': (lambda self, cr, uid, ids, context=None:
                            ids, ['partner_id'], 20),
    }

    def _compute_unique_id(self, cr, uid, ids, fname, arg, context=None):
        return super(sta_mandate, self)._compute_unique_id(cr, uid, ids,
                                                           fname,
                                                           arg,
                                                           context=context)

    _columns = {
        'unique_id': fields.function(
                                     _compute_unique_id,
                                     type="integer",
                                     string="Unique id",
                                     store=_unique_id_store_trigger),
        'mandate_category_id': fields.many2one(
                                     'mandate.category',
                                     string='Mandate Category',
                                     select=True,
                                     required=True,
                                     track_visibility='onchange',
                                     domain=[('type', '=', 'sta')]),
        'legislature_id': fields.many2one(
                                     'legislature',
                                     string='Legislature',
                                     select=True,
                                     required=True,
                                     track_visibility='onchange'),
        'sta_assembly_id': fields.many2one(
                                     'sta.assembly',
                                     string='State Assembly',
                                     select=True,
                                     required=True),
        'sta_assembly_category_id': fields.related(
                                     'mandate_category_id',
                                     'sta_assembly_category_id',
                                     string='State Assembly Category',
                                     type='many2one',
                                     relation="sta.assembly.category",
                                     store=False),
        'sta_power_level_id': fields.related(
                                     'sta_assembly_category_id',
                                     'power_level_id',
                                     string='Power Level',
                                     type='many2one',
                                     relation="sta.power.level",
                                     store=False),
        'candidature_id': fields.many2one(
                                     'sta.candidature',
                                     'Candidature'),
        'is_submission_mandate': fields.related(
                                 'mandate_category_id',
                                 'is_submission_mandate',
                                 string='With Wages Declaration',
                                 help='Submission to a Mandates and Wages Declaration',
                                 type='boolean',
                                 store={'mandate.category':
                                 (mandate_category.get_linked_sta_mandate_ids,
                                 ['is_submission_mandate'], 20)}),
        'is_submission_assets': fields.related(
                                 'mandate_category_id',
                                 'is_submission_assets',
                                 string='With Assets Declaration',
                                 help='Submission to a Mandates and Assets Declaration',
                                 type='boolean',
                                 store={'mandate.category':
                                 (mandate_category.get_linked_sta_mandate_ids,
                                 ['is_submission_assets'], 20)}),
        'is_legislative': fields.related(
                                     'sta_assembly_id',
                                     'is_legislative',
                                     string='Is Legislative',
                                     type='boolean',
                                     store=True),
        'competencies_m2m_ids': fields.many2many(
                                     'thesaurus.term',
                                     'sta_mandate_term_competencies_rel',
                                     id1='sta_mandate_id',
                                     id2='thesaurus_term_id',
                                     string='Competencies'),
    }

    _order = 'partner_id, sta_assembly_id, legislature_id, mandate_category_id'

# constraints

    _unicity_keys = 'partner_id, sta_assembly_id, legislature_id,\
                     mandate_category_id'

# view methods: onchange, button

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
        return super(sta_mandate, self).action_invalidate(cr, uid, ids,
                                                          context=context,
                                                          vals=vals)

    def action_finish(self, cr, uid, ids, context=None):
        """
        =================
        action_finish
        =================
        Finish mandate at the current date
        :rparam: True
        :rtype: boolean
        """
        return super(sta_mandate, self).action_finish(cr, uid, ids,
                                                      context=context)

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id,
                                     context=None):
        sta_assembly_category_id = False

        if mandate_category_id:
            category_data = self.pool.get('mandate.category').read(
                                               cr,
                                               uid,
                                               mandate_category_id,
                                               ['sta_assembly_category_id'],
                                               context)
            sta_assembly_category_id = category_data[\
                                           'sta_assembly_category_id'] or False

        res = {
            'sta_assembly_category_id': sta_assembly_category_id,
            'sta_assembly_id': False,
            'legislature_id': False,
        }
        return {
            'value': res,
        }

    def onchange_legislature_id(self, cr, uid, ids, legislature_id,
                                context=None):
        res = {}
        res['value'] = dict(mandate_start_date=False,
                            mandate_deadline_date=False)
        if legislature_id:
            legislature_data = self.pool.get('legislature').read(
                                                             cr,
                                                             uid,
                                                             legislature_id,
                                                             ['start_date',
                                                              'deadline_date'])
            res['value'] = dict(
                            start_date=legislature_data['start_date'],
                            deadline_date=legislature_data['deadline_date'])
        return res

    def onchange_sta_assembly_id(self, cr, uid, ids, sta_assembly_id,
                                 context=None):
        res = {}
        res['value'] = dict(sta_power_level_id=False)
        if sta_assembly_id:
            assembly = self.pool.get('sta.assembly').browse(cr, uid,
                                                            sta_assembly_id)

            res['value'] = dict(
            sta_power_level_id=assembly.assembly_category_id.power_level_id.id)

        return res
