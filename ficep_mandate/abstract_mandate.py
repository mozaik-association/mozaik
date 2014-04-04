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

    def _compute_name(self, cr, uid, ids, fname, arg, context=None):
        res = {}
        mandates = self.browse(cr, uid, ids, context=context)
        for mandate in mandates:
            fullname = "%s (%s)" % (mandate.partner_name if mandate.partner_name else mandate.partner_id.name, mandate.mandate_category_id.name)
            res[mandate.id] = fullname
        return res

    _name_store_triggers = True

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.function(_compute_name, string="Name",
                                 type="char", store=_name_store_triggers,
                                 select=True, track_visibility='onchange'),
        'deadline_date': fields.date('Deadline Date', required=True, track_visibility='onchange'),
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, track_visibility='onchange'),
        'partner_name': fields.char('Partner Name', size=128, translate=True, select=True, track_visibility='onchange'),
        'is_replacement': fields.boolean('Replacement'),
    }


class abstract_mandate(orm.AbstractModel):

    _name = 'abstract.mandate'
    _description = "Abstract Mandate"
    _inherit = ['abstract.mandate.base']

    _columns = {
        'is_submission_mandate': fields.related('mandate_category_id', 'submission_mandate', string='Submission to a mandate declaration',
                                          type='boolean', relation="mandate.category",
                                          store=True),
        'is_submission_assets': fields.related('mandate_category_id', 'submission_assets', string='Submission to an assets declaration',
                                          type='boolean', relation="mandate.category",
                                          store=True),
    }


class abstract_candidature(orm.AbstractModel):

    _name = 'abstract.candidature'
    _description = "Abstract Candidature"
    _inherit = ['abstract.mandate.base']

    _columns = {
        'state': fields.selection(CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'selection_committee_id': fields.many2one('selection.committee', string='Selection Committee',
                                                 required=True, track_visibility='onchange'),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
