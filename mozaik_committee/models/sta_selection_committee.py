# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StaSelectionCommittee(models.Model):
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
        'mandate_category_id': fields.many2one(
            'mandate.category',
            string='Mandate Category',
            required=True,
            track_visibility='onchange',
            domain=[
                ('type',
                 '=',
                 'sta')]),
        'assembly_id': fields.many2one(
            _assembly_model,
            string='State Assembly',
            track_visibility='onchange'),
        'candidature_ids': fields.one2many(
            _candidature_model,
            'selection_committee_id',
            'State Candidatures',
            domain=[
                ('active',
                 '<=',
                 True)],
            context={
                'force_recompute': True}),
        'assembly_category_id': fields.related(
            'mandate_category_id',
            _mandate_category_foreign_key,
            string='State Assembly Category',
            type='many2one',
            relation=_assembly_category_model,
            store=False),
        'electoral_district_id': fields.many2one(
            'electoral.district',
            string='Electoral District',
            track_visibility='onchange'),
        'legislature_id': fields.many2one(
            'legislature',
            string='Legislature',
            track_visibility='onchange'),
        'listname': fields.char(
            'Name',
            size=128,
            track_visibility='onchange'),
        'is_cartel': fields.boolean('Is Cartel'),
        'cartel_composition': fields.text(
            'Cartel composition',
            track_visibility='onchange'),
        'partner_ids': fields.many2many(
            'res.partner',
            'sta_selection_committee_res_partner_rel',
            'committee_id',
            'partner_id',
            string='Members',
            domain=[
                ('is_company',
                 '=',
                 False)]),
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
                assembly=committee.electoral_district_id.name or
                         committee.assembly_id.name,
                start=self.pool.get('res.lang').format_date(
                    cr,
                    uid,
                    committee.mandate_start_date,
                    context) or False,
                name=committee.name, )
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
            'mandate_start_date': legislature_data['value'][
                'mandate_start_date'],
            'mandate_deadline_date': legislature_data['value'][
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
        return super(sta_selection_committee, self).action_copy(
            cr, uid, ids, context=context)

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
            res['value'] = dict(assembly_id=district_data['assembly_id'],
                                designation_int_assembly_id=district_data[
                                    'designation_int_assembly_id'])
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
            res['value'] = dict(mandate_start_date=legislature_data[
                'start_date'],
                                mandate_deadline_date=legislature_data[
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
            legislature_ids = self.pool.get('legislature').search(
                cr,
                uid,
                [
                    ('power_level_id',
                     '=',
                     assembly.assembly_category_id.power_level_id.id),
                    ('start_date',
                     '>',
                     fields.datetime.now())])
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
