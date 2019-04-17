# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _, SUPERUSER_ID


CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('rejected', 'Rejected'),
    ('suggested', 'Suggested'),
    ('designated', 'Designated'),
    ('elected', 'Elected'),
    ('non-elected', 'Non-Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)


class AbstractCandidature(models.Model):
    _name = 'abstract.candidature'
    _description = 'Abstract Candidature'
    _inherit = ['mozaik.abstract.model']

    _init_mandate_columns = ['mandate_category_id',
                             'partner_id',
                             'designation_int_assembly_id']
    _mandate_model = 'abstract.mandate'
    _mandate_form_view = 'abstract_mandate_form_view'

    _mandate_category_store_trigger = {}
    _designation_assembly_store_trigger = {}
    _mandate_start_date_store_trigger = {}

    _columns = {
        'unique_id': fields.integer("Unique id", group_operator='min'),
        'partner_id': fields.many2one('res.partner',
                                      'Candidate',
                                      required=True,
                                      select=True,
                                      track_visibility='onchange'),
        'partner_name': fields.char('Candidate Name',
                                    size=128,
                                    required=True,
                                    track_visibility='onchange'),
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES,
                                  'Status',
                                  readonly=True,
                                  track_visibility='onchange', ),
        'selection_committee_id': fields.many2one(
            'abstract.selection.committee',
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
            store=_mandate_category_store_trigger),
        'designation_int_assembly_id': fields.related(
            'selection_committee_id',
            'designation_int_assembly_id',
            string='Designation Assembly',
            type='many2one',
            relation="int.assembly",
            store=_designation_assembly_store_trigger,
            domain=[
                ('is_designation_assembly', '=', True)
            ]),
        'is_selection_committee_active': fields.related(
            'selection_committee_id',
            'active',
            string='Is Selection Committee Active?',
            type='boolean'),
        'mandate_ids': fields.one2many(_mandate_model,
                                       'candidature_id',
                                       'Abstract Mandates',
                                       domain=[('active', '<=', True)]),
    }

    _defaults = {
        'state': CANDIDATURE_AVAILABLE_STATES[0][0],
    }

    # constraints

    def _check_partner(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_partner
        =================
        Check if partner doesn't have several candidatures in the same category
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        uid = SUPERUSER_ID
        candidatures = self.browse(cr, uid, ids)
        for candidature in candidatures:
            if len(self.search(cr,
                               uid,
                               [('partner_id',
                                 '=', candidature.partner_id.id),
                                ('id', '!=', candidature.id),
                                ('mandate_category_id',
                                 '=',
                                 candidature.mandate_category_id.id)],
                               context=context)) > 0:
                return False

        return True

    _constraints = [
        (_check_partner,
         _("A candidature already exists for this partner in this category"),
         ['partner_id'])
    ]

    _unicity_keys = 'selection_committee_id, partner_id'

    # orm methods

    def create(self, cr, uid, vals, context=None):
        if ('partner_name' not in vals) or \
                ('partner_name' in vals and not vals['partner_name']):
            vals['partner_name'] = self.onchange_partner_id(
                cr,
                uid,
                False,
                vals['partner_id'],
                context
            )['value']['partner_name']

        res = super(abstract_candidature, self).create(cr,
                                                       uid,
                                                       vals,
                                                       context=context)
        self.write(cr, uid, res, {'unique_id': res + self._unique_id_sequence})
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for candidature in self.browse(cr, uid, ids, context=context):
            display_name = u'{name} ({mandate_category})'.format(
                name=candidature.partner_name or candidature.partner_id.name,
                mandate_category=candidature.mandate_category_id.name)
            res.append((candidature['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            partner_ids = self.pool.get('res.partner').search(cr,
                                                              uid,
                                                              [('name',
                                                                operator,
                                                                name)],
                                                              context=context)
            category_ids = self.pool.get('mandate.category').search(
                cr,
                uid,
                [('name',
                  operator,
                  name)],
                context=context)
            ids = self.search(cr, uid, ['|',
                                        '|',
                                        ('partner_name', operator, name),
                                        ('partner_id', 'in', partner_ids),
                                        ('mandate_category_id',
                                         'in', category_ids)] + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    # view methods: onchange, button

    def action_elected(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'elected'})
        for candidature in self.browse(cr, uid, ids, context):
            if candidature.selection_committee_id.auto_mandate:
                self.create_mandate_from_candidature(cr,
                                                     uid,
                                                     candidature.id,
                                                     context)
        return True

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = {}
        partner_model = self.pool.get('res.partner')
        partner = partner_model.browse(cr, uid, partner_id, context)

        res['value'] = dict(
            partner_name=partner_model.build_name(
                partner,
                capitalize_mode=True) or False)
        return res

    def button_create_mandate(self, cr, uid, ids, context=None):
        for candidature_id in ids:
            mandate_id = self.create_mandate_from_candidature(cr,
                                                              uid,
                                                              candidature_id,
                                                              context)

        return self.pool.get(self._mandate_model).display_object_in_form_view(
            cr,
            uid,
            mandate_id,
            context=context)

    def create_mandate_from_candidature(self, cr, uid, candidature_id,
                                        context=None):
        """
        ==============================
        create_mandate_from_candidature
        ==============================
        Return Mandate id create on base of candidature id
        :rparam: mandate id
        :rtype: id
        """
        mandate_pool = self.pool.get(self._mandate_model)
        committee_pool = self.pool.get(self._selection_committee_model)
        candidature_data = self.read(cr, uid, candidature_id, [], context)
        res = False
        mandate_values = {}
        for column in self._init_mandate_columns:
            if column in mandate_pool._columns:
                if self._columns[column]._type == 'many2one':
                    mandate_values[column] = candidature_data[column][0]
                else:
                    mandate_values[column] = candidature_data[column]

        if mandate_values:
            committee_data = committee_pool.read(
                cr,
                uid,
                candidature_data['selection_committee_id'][0],
                ['mandate_start_date',
                 'mandate_deadline_date'],
                context=context)
            mandate_values['start_date'] = committee_data['mandate_start_date']
            mandate_values['deadline_date'] = \
                committee_data['mandate_deadline_date']
            mandate_values['candidature_id'] = candidature_data['id']
            res = mandate_pool.create(cr, uid, mandate_values, context)
        return res
