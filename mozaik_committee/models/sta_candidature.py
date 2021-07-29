# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

CANDIDATURE_AVAILABLE_SORT_ORDERS = {
    'elected': 0,
    'non-elected': 10,
    'designated': 20,
    'suggested': 22,
    'declared': 24,
    'rejected': 30,
    'draft': 90,
}


class StaCandidature(models.Model):
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
         "A candidature already exists for this partner in this category",
         ['partner_id'])
    ]

    # view methods: onchange, button

    def onchange_selection_committee_id(self, cr, uid, ids,
                                        selection_committee_id, context=None):
        res = {}
        selection_committee = False
        if selection_committee_id:
            selection_committee = \
                self.pool.get(self._selection_committee_model).browse(
                    cr,
                    uid,
                    selection_committee_id,
                    context)

        res['value'] = dict(
            legislature_id=selection_committee and
                           selection_committee.legislature_id.id,
            electoral_district_id=selection_committee and
                                  selection_committee.electoral_district_id.id,
            sta_assembly_id=selection_committee and
                            selection_committee.assembly_id.id,
            designation_int_assembly_id=selection_committee and
                                        selection_committee.designation_int_assembly_id.id,
            mandate_category_id=selection_committee and
                                selection_committee.mandate_category_id.id,
            is_legislative=selection_committee and
                           selection_committee.assembly_id.is_legislative, )
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
