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

# Constants
MANDATE_CATEGORY_AVAILABLE_TYPES = [
    ('sta', 'State'),
    ('int', 'Internal'),
    ('ext', 'External'),
]

mandate_category_available_types = dict(MANDATE_CATEGORY_AVAILABLE_TYPES)


class mandate_category(orm.Model):

    _name = 'mandate.category'
    _description = 'Mandate Category'
    _inherit = ['abstract.ficep.model']

    def get_linked_sta_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_sta_mandate_ids
        ==============================
        Return State Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        return self._get_linked_mandate_ids(cr, uid, ids, 'sta_mandate_ids', context=context)

    def get_linked_int_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_int_mandate_ids
        ==============================
        Return Internal Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        return self._get_linked_mandate_ids(cr, uid, ids, 'int_mandate_ids', context=context)

    def get_linked_ext_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_ext_mandate_ids
        ==============================
        Return External Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        return self._get_linked_mandate_ids(cr, uid, ids, 'ext_mandate_ids', context=context)

    def _get_linked_mandate_ids(self, cr, uid, ids, mandate_relation, context=None):
        """
        ==============================
        get_linked_mandate_ids
        ==============================
        Return State Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        mandate_categories = self.read(cr, uid, ids, [mandate_relation], context=context)
        res_ids = []
        for mandate_category in mandate_categories:
            res_ids += mandate_category[mandate_relation]
        return list(set(res_ids))

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'type': fields.selection(MANDATE_CATEGORY_AVAILABLE_TYPES, 'Status', readonly=True),
        'exclusive_category_m2m_ids': fields.many2many('mandate.category', 'mandate_category_mandate_category_rel', 'id', 'exclu_id',
                                                      'Exclusive Category'),
        'sta_assembly_category_id': fields.many2one('sta.assembly.category', string='State Assembly Category', track_visibility='onchange'),
        'ext_assembly_category_id': fields.many2one('ext.assembly.category', string='External Assembly Category', track_visibility='onchange'),
        'int_assembly_category_id': fields.many2one('int.assembly.category', string='Internal Assembly Category', track_visibility='onchange'),
        'int_power_level_id': fields.many2one('int.power.level', string='Internal Power Level',
                                                 required=True, track_visibility='onchange'),
        'sta_mandate_ids': fields.one2many('sta.mandate', 'mandate_category_id', 'State Mandates'),
        'int_mandate_ids': fields.one2many('int.mandate', 'mandate_category_id', 'Internal Mandates'),
        'ext_mandate_ids': fields.one2many('ext.mandate', 'mandate_category_id', 'External Mandates'),
        'is_submission_mandate': fields.boolean('Submission to a Mandate Declaration'),
        'is_submission_assets': fields.boolean('Submission to an Assets Declaration'),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'name'
