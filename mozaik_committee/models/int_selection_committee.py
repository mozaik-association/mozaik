# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IntSelectionCommittee(models.Model):
    _name = 'int.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    _candidature_model = 'int.candidature'
    _assembly_model = 'int.assembly'
    _assembly_category_model = 'int.assembly.category'
    _mandate_category_foreign_key = 'int_assembly_category_id'
    _form_view = 'int_selection_committee_form_view'
    _parameters_key = 'int_candidature_invalidation_delay'

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        return super(int_selection_committee,
                     self)._get_suggested_candidatures(cr,
                                                       uid,
                                                       ids,
                                                       context=context)

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category',
                                               string='Mandate Category',
                                               required=True,
                                               track_visibility='onchange',
                                               domain=[('type', '=', 'int')]),
        'is_virtual': fields.boolean('Is Virtual'),
        'assembly_id': fields.many2one(_assembly_model,
                                       string='Internal Assembly',
                                       track_visibility='onchange',
                                       domain=[
                                           ('designation_int_assembly_id',
                                            '!=', False)]),
        'candidature_ids': fields.one2many(_candidature_model,
                                           'selection_committee_id',
                                           'Internal Candidatures',
                                           domain=[('active', '<=', True)],
                                           context={'force_recompute': True}),
        'assembly_category_id': fields.related(
            'mandate_category_id',
            _mandate_category_foreign_key,
            string='Internal Assembly Category',
            type='many2one',
            relation=_assembly_category_model,
            store=False),
        'partner_ids': fields.many2many(
            'res.partner', 'int_selection_committee_res_partner_rel',
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
        Duplicate committee and keep rejected internal candidatures
        :rparam: True
        :rtype: boolean
        """
        return super(int_selection_committee,
                     self).action_copy(cr, uid, ids, context=context)

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
        return super(int_selection_committee,
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
        return super(int_selection_committee,
                     self).button_refuse_candidatures(cr,
                                                      uid,
                                                      ids,
                                                      context=context)

    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        return super(int_selection_committee,
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
        return super(int_selection_committee,
                     self).process_invalidate_candidatures_after_delay(
            cr,
            uid,
            context=context)
