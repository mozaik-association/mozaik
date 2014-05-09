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
from openerp.osv import orm, osv, fields
from openerp.tools.translate import _

from openerp.addons.ficep_mandate.mandate import mandate_category

SELECTION_COMMITTEE_AVAILABLE_STATES = [
    ('draft', 'In Progress'),
    ('done', 'Closed'),
]
selection_committee_available_states = dict(SELECTION_COMMITTEE_AVAILABLE_STATES)

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


def create_mandate_from_candidature(cr, uid, candidature_pool, candidature_id, context=None):
    """
    ==============================
    create_mandate_from_candidature
    ==============================
    Return Mandate id create on base of candidature id
    :rparam: mandate id
    :rtype: id
    """
    mandate_pool = candidature_pool.pool.get(candidature_pool._mandate_model)
    committee_pool = candidature_pool.pool.get(candidature_pool._selection_committee_model)
    candidature_data = candidature_pool.read(cr, uid, candidature_id, [], context)
    res = False
    mandate_values = {}
    for column in candidature_pool._init_mandate_columns:
        if column in mandate_pool._columns:
            if candidature_pool._columns[column]._type == 'many2one':
                mandate_values[column] = candidature_data[column][0]
            else:
                mandate_values[column] = candidature_data[column]

    if mandate_values:
        committee_data = committee_pool.read(cr, uid, candidature_data['selection_committee_id'][0], ['mandate_start_date', 'mandate_deadline_date'], context=context)
        mandate_values['start_date'] = committee_data['mandate_start_date']
        mandate_values['deadline_date'] = committee_data['mandate_deadline_date']
        mandate_values['candidature_id'] = candidature_data['id']
        candidature_pool.action_invalidate(cr, uid, candidature_id, context=context)
        res = mandate_pool.create(cr, uid, mandate_values, context)
    return res


class abstract_selection_committee(orm.AbstractModel):
    _name = 'abstract.selection.committee'
    _description = 'Abstract Selection Committee'
    _inherit = ['abstract.ficep.model']

    _candidature_model = 'abstract.candidature'
    _assembly_model = 'abstract.assembly'
    _assembly_category_model = 'abstract.assembly.category'
    _mandate_category_foreign_key = False
    _form_view = 'abstract_selection_committee_form_view'

    def _get_suggested_candidatures(self, cr, uid, ids, context=None):
        """
        ==============================
        _get_suggested_candidatures
        ==============================
        Return list of candidature ids in suggested state
        :rparam: committee id
        :rtype: list of ids
        """
        res = []
        committee = self.browse(cr, uid, ids[0], context=context)
        for candidature in committee.candidature_ids:
            if candidature.state == 'rejected':
                continue
            elif candidature.state == 'suggested':
                res.append(candidature.id)
            else:
                raise osv.except_osv(_('Operation Forbidden!'),
                             _('All candidatures are not in suggested state'))
        return res

    _columns = {
        'state': fields.selection(SELECTION_COMMITTEE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange'),
        'assembly_id': fields.many2one(_assembly_model, string='Abstract Assembly', track_visibility='onchange'),
        'candidature_ids': fields.one2many(_candidature_model, 'selection_committee_id', 'Abstract Candidatures',
                                               domain=[('active', '<=', True)]),
        'assembly_category_id': fields.related('mandate_category_id', _mandate_category_foreign_key, string='Abstract Assembly Category',
                                          type='many2one', relation=_assembly_category_model,
                                          store=False),
        'designation_int_assembly_id': fields.many2one('int.assembly', string='Designation Assembly',
                                                 required=True, track_visibility='onchange', domain=[('is_designation_assembly', '=', True)]),
        'decision_date': fields.date('Designation Date', track_visibility='onchange'),
        'mandate_start_date': fields.date('Start Date of Mandates', required=True, track_visibility='onchange'),
        'mandate_deadline_date': fields.date('Deadline Date of Mandates', required=True, track_visibility='onchange'),
        'meeting_date': fields.date('Committee Meeting Date', track_visibility='onchange'),
        'name': fields.char('Name', size=128, translate=True, select=True, required=True, track_visibility='onchange'),
        'partner_ids': fields.many2many('res.partner', 'selection_committee_res_partner_rel', 'id', 'member_id',
                                                      'Members', domain=[('is_company', '=', False)]),
        'note': fields.text('Notes', track_visibility='onchange'),
        'auto_mandate': fields.boolean("Create Mandates after Election"),
    }

    _defaults = {
        'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
        'auto_mandate': False,
    }

    # orm methods
    def copy_data(self, cr, uid, id_, default=None, context=None):
        default = default or {}

        default.update({
            'active': True,
            'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
            'note': False,
            'decision_date': False,
            'meeting_date': False,
            'candidature_ids': False,
        })
        res = super(abstract_selection_committee, self).copy_data(cr, uid, id_, default=default, context=context)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res

    # view methods: onchange, button
    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected candidatures
        :rparam: True
        :rtype: boolean
        """
        copied_committee_id = ids[0]
        candidature_pool = self.pool.get(self._candidature_model)
        rejected_candidature_ids = candidature_pool.search(cr, uid, [('selection_committee_id', '=', copied_committee_id),
                                                                                     ('state', '=', 'rejected')])
        new_committee_id = self.copy(cr, uid, copied_committee_id, None, context)
        if rejected_candidature_ids:
            candidature_pool.write(cr, uid, rejected_candidature_ids, {'selection_committee_id': new_committee_id})
            candidature_pool.signal_button_declare(cr, uid, rejected_candidature_ids)

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_mandate', self._form_view)
        view_id = view_ref and view_ref[1] or False,

        return {
            'type': 'ir.actions.act_window',
            'name': _('Selection Committee'),
            'res_model': candidature_pool._selection_committee_model,
            'res_id': new_committee_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def button_accept_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_accept_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        for committee in self.browse(cr, uid, ids, context=context):
            if committee.candidature_ids:
                self.pool.get(self._candidature_model).signal_action_accept(cr, uid, self._get_suggested_candidatures(cr, uid, ids, context=context))
        self.action_invalidate(cr, uid, ids, context, {'state': 'done'})
        return True

    def button_refuse_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_refuse_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        for committee in self.browse(cr, uid, ids, context=context):
            if committee.candidature_ids:
                self.pool.get(self._candidature_model).signal_button_declare(cr, uid, self._get_suggested_candidatures(cr, uid, ids, context=context))
            self.write(cr, uid, ids, {'decision_date': False}, context=context)
        return True

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        res = {}
        assembly_category_id = False
        if mandate_category_id:
            mandate_category = self.pool.get('mandate.category').browse(cr, uid, mandate_category_id, context)
            values = dict(sta_assembly_category_id=mandate_category.sta_assembly_category_id.id or False,
                                int_assembly_category_id=mandate_category.int_assembly_category_id.id or False,
                                ext_assembly_category_id=mandate_category.ext_assembly_category_id.id or False,
                                )
            assembly_category_id = values[self._mandate_category_foreign_key]
        res['value'] = dict(assembly_category_id=assembly_category_id)
        return res

    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        res = {}
        res['value'] = dict(assembly_category_id=False,
                            mandate_category_id=False)
        if assembly_id:
            assembly = self.pool.get(self._assembly_model).browse(cr, uid, assembly_id)
            mandate_category_ids = self.pool.get('mandate.category').search(cr, uid, [(self._mandate_category_foreign_key, '=', assembly.assembly_category_id.id)])
            mandate_category_id = False
            if mandate_category_ids:
                mandate_category_id = mandate_category_ids[0]

            res['value'] = dict(assembly_category_id=assembly.assembly_category_id.id or False,
                                mandate_category_id=mandate_category_id)
        return res


class abstract_mandate_base(orm.AbstractModel):

    _name = 'abstract.mandate.base'
    _description = "Abstract Mandate Base"
    _inherit = ['abstract.ficep.model']

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, select=True, track_visibility='onchange'),
        'is_replacement': fields.boolean('Replacement'),
    }


class abstract_mandate(orm.AbstractModel):

    _name = 'abstract.mandate'
    _description = 'Abstract Mandate'
    _inherit = ['abstract.mandate.base']

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one('int.assembly', 'Designation Assembly', required=True,
                                                       track_visibility='onchange', domain=[('is_designation_assembly', '=', True)]),
        'start_date': fields.date('Start Date', required=True, track_visibility='onchange'),
        'deadline_date': fields.date('Deadline Date', required=True, track_visibility='onchange'),
        'end_date': fields.date('End Date', track_visibility='onchange'),
        'is_submission_mandate': fields.related('mandate_category_id', 'is_submission_mandate', string='Submission to a Mandate Declaration',
                                          type='boolean', store=True),
        'is_submission_assets': fields.related('mandate_category_id', 'is_submission_assets', string='Submission to an Assets Declaration',
                                          type='boolean', store=True),
        'candidature_id': fields.many2one('abstract.candidature', 'Candidature', track_visibility='onchange'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),
    }

    _defaults = {
        'end_date': False,
    }

# constraints

    _unicity_keys = 'partner_id, mandate_category_id, start_date'

# view methods: onchange, button

    def action_finish(self, cr, uid, ids, context=None):
        """
        =================
        action_finish
        =================
        Finish mandate at the current date
        :rparam: True
        :rtype: boolean
        """
        for mandate_id in ids:
            self.write(cr, uid, mandate_id, {'end_date': fields.datetime.now()}, context=context)

        return True

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
        res = super(abstract_mandate, self).action_invalidate(cr, uid, ids, context=context, vals=vals)
        for mandate in self.browse(cr, uid, ids, context=context):
            if mandate.email_coordinate_id:
                self.pool.get('email.coordinate').action_invalidate(cr, uid, [mandate.email_coordinate_id.id])
            if mandate.postal_coordinate_id:
                self.pool.get('postal.coordinate').action_invalidate(cr, uid, [mandate.postal_coordinate_id.id])
        return res

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for mandate in self.browse(cr, uid, ids, context=context):
            display_name = u'{name} {mandate_category}'.format(name=mandate.partner_id.name,
                                                               mandate_category=mandate.mandate_category_id.name)
            res.append((mandate['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('name', operator, name)], context=context)
            category_ids = self.pool.get('mandate.category').search(cr, uid, [('name', operator, name)], context=context)
            ids = self.search(cr, uid, ['|', ('partner_id', 'in', partner_ids), ('mandate_category_id', 'in', category_ids)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)


class abstract_candidature(orm.AbstractModel):

    _name = 'abstract.candidature'
    _description = "Abstract Candidature"
    _inherit = ['abstract.mandate.base']

    _init_mandate_columns = ['mandate_category_id', 'partner_id', 'is_replacement', 'designation_int_assembly_id']
    _mandate_model = 'abstract.mandate'

    _columns = {
        'partner_name': fields.char('Partner Name', size=128, required=True, track_visibility='onchange'),
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one('abstract.selection.committee', string='Selection Committee',
                                                 required=True, select=True, track_visibility='onchange'),
        'mandate_category_id': fields.related('selection_committee_id', 'mandate_category_id', string='Mandate Category',
                                          type='many2one', relation="mandate.category",
                                          store=True),
        'designation_int_assembly_id': fields.related('selection_committee_id', 'designation_int_assembly_id', string='Designation Assembly',
                                          type='many2one', relation="int.assembly",
                                          store=True),
        'is_selection_committee_active': fields.related('selection_committee_id', 'active', string='Is Selection Committee Active ?',
                                          type='boolean', store=False),
    }

    _defaults = {
        'state': CANDIDATURE_AVAILABLE_STATES[0][0],
    }

    _order = 'selection_committee_id, partner_id'

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
        candidatures = self.browse(cr, uid, ids)
        for candidature in candidatures:
            if len(self.search(cr, uid, [('partner_id', '=', candidature.partner_id.id), ('id', '!=', candidature.id), ('mandate_category_id', '=', candidature.mandate_category_id.id)], context=context)) > 0:
                return False

        return True

    _constraints = [
        (_check_partner, _("A candidature already exists for this partner in this category"), ['partner_id'])
    ]

    _unicity_keys = 'selection_committee_id, partner_id'

# orm methods

    def create(self, cr, uid, vals, context=None):
        if ('partner_name' not in vals) or ('partner_name' in vals and not vals['partner_name']):
            vals['partner_name'] = self.onchange_partner_id(cr, uid, False, vals['partner_id'], context)['value']['partner_name']

        res = super(abstract_candidature, self).create(cr, uid, vals, context=context)
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for candidature in self.browse(cr, uid, ids, context=context):
            display_name = u'{name} {mandate_category}'.format(name=candidature.partner_name or candidature.partner_id.name,
                                                               mandate_category=candidature.mandate_category_id.name)
            res.append((candidature['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('name', operator, name)], context=context)
            category_ids = self.pool.get('mandate.category').search(cr, uid, [('name', operator, name)], context=context)
            ids = self.search(cr, uid, ['|', '|', ('partner_name', operator, name), ('partner_id', 'in', partner_ids), ('mandate_category_id', 'in', category_ids)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# view methods: onchange, button
    def action_elected(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'elected'})
        for candidature in self.browse(cr, uid, ids, context):
            if candidature.selection_committee_id.auto_mandate:
                create_mandate_from_candidature(cr, uid, self, candidature.id, context)
        return True

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = {}
        partner_model = self.pool.get('res.partner')
        partner = partner_model.browse(cr, uid, partner_id, context)

        res['value'] = dict(partner_name=partner_model.build_name(partner, False, False) or False,)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
