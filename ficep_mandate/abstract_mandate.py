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
from .mandate import mandate_category

CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('suggested', 'Suggested'),
    ('designated', 'Designated'),
    ('rejected', 'Rejected'),
    ('elected', 'Elected'),
    ('non-elected', 'Non-Elected'),
]

candidature_available_states = dict(CANDIDATURE_AVAILABLE_STATES)


class abstract_mandate_base(orm.AbstractModel):
    _name = 'abstract.mandate.base'
    _description = "Abstract Mandate Base"
    _inherit = ['abstract.ficep.model']

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, track_visibility='onchange'),
        'is_replacement': fields.boolean('Replacement'),
    }


class abstract_mandate(orm.AbstractModel):

    _name = 'abstract.mandate'
    _description = "Abstract Mandate"
    _inherit = ['abstract.mandate.base']

    _columns = {
        'deadline_date': fields.date('Deadline Date', required=True, track_visibility='onchange'),
        'is_submission_mandate': fields.related('mandate_category_id', 'submission_mandate', string='Submission to a mandate declaration',
                                          type='boolean', relation="mandate.category",
                                          store={'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['is_submission_mandate'], 20)}),
        'is_submission_assets': fields.related('mandate_category_id', 'submission_assets', string='Submission to an assets declaration',
                                          type='boolean', relation="mandate.category",
                                          store={'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['is_submission_assets'], 20)}),
    }

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

    _init_mandate_columns = ['mandate_category_id', 'partner_id', 'is_replacement']

    _columns = {
        'partner_name': fields.char('Partner Name', size=128, translate=True, select=True, track_visibility='onchange'),
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one('selection.committee', string='Selection Committee',
                                                 required=True, track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one('int.assembly', 'Designation assembly', required=True, track_visibility='onchange'),
    }

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

    _defaults = {
        'state': CANDIDATURE_AVAILABLE_STATES[0][0],
    }

# orm methods
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
