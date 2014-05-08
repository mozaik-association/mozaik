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
    committee_pool = candidature_pool.pool.get('selection.committee')
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


class abstract_mandate(orm.AbstractModel):

    _name = 'abstract.mandate'
    _description = 'Abstract Mandate'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Representative', required=True, select=True, track_visibility='onchange'),
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
        'is_replacement': fields.boolean('Replacement'),
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
    _description = 'Abstract Candidature'
    _inherit = ['abstract.ficep.model']

    _init_mandate_columns = ['mandate_category_id', 'partner_id', 'designation_int_assembly_id']
    _mandate_model = 'abstract.mandate'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Candidate', required=True, select=True, track_visibility='onchange'),
        'partner_name': fields.char('Candidate Name', size=128, required=True, track_visibility='onchange'),
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one('selection.committee', string='Selection Committee',
                                                 required=True, select=True, track_visibility='onchange'),
        'mandate_category_id': fields.related('selection_committee_id', 'mandate_category_id', string='Mandate Category',
                                          type='many2one', relation="mandate.category",
                                          store=True),
        'designation_int_assembly_id': fields.related('selection_committee_id', 'designation_int_assembly_id', string='Designation Assembly',
                                          type='many2one', relation="int.assembly",
                                          store=True),
    }

    _defaults = {
        'state': CANDIDATURE_AVAILABLE_STATES[0][0],
    }

    _order = 'selection_committee_id, partner_name'

# constraints

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

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = {}
        partner_model = self.pool.get('res.partner')
        partner = partner_model.browse(cr, uid, partner_id, context)

        res['value'] = dict(partner_name=partner_model.build_name(partner, capitalize_mode=True) or False,)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
