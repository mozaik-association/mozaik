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


class ext_selection_committee(orm.Model):
    _name = 'ext.selection.committee'
    _description = 'Selection Committee'
    _inherit = ['abstract.selection.committee']

    _candidature_model = 'ext.candidature'
    _assembly_model = 'ext.assembly'
    _assembly_category_model = 'ext.assembly.category'
    _mandate_category_foreign_key = 'ext_assembly_category_id'
    _form_view = 'ext_selection_committee_form_view'

    _columns = {
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                         required=True, track_visibility='onchange', domain=[('type', '=', 'ext')]),
        'is_virtual': fields.boolean('Is Virtual'),
        'assembly_id': fields.many2one(_assembly_model, string='External Assembly', track_visibility='onchange'),
        'candidature_ids': fields.one2many(_candidature_model, 'selection_committee_id', 'External Candidatures',
                                               domain=[('active', '<=', True)]),
        'assembly_category_id': fields.related('mandate_category_id', 'assembly_category_id', string='External Assembly Category',
                                          type='many2one', relation=_assembly_category_model,
                                          store=False),
    }

    _defaults = {
        'is_virtual': False,
    }

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
        return super(ext_selection_committee, self).action_copy(cr, uid, ids, context=context)

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
        return super(ext_selection_committee, self).button_accept_candidatures(cr, uid, ids, context=context)

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
        return super(ext_selection_committee, self).button_refuse_candidatures(cr, uid, ids, context=context)

# constraints

    _unicity_keys = 'N/A'

    # view methods: onchange, button
    def onchange_assembly_id(self, cr, uid, ids, assembly_id, context=None):
        return super(ext_selection_committee, self).onchange_assembly_id(cr, uid, ids, assembly_id, context=None)