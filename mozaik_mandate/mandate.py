# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _

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
    _inherit = ['mozaik.abstract.model']

    def get_linked_sta_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_sta_mandate_ids
        ==============================
        Return State Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        return self._get_linked_mandate_ids(cr, uid, ids, 'sta_mandate_ids',
                                            context=context)

    def get_linked_int_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_int_mandate_ids
        ==============================
        Return Internal Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        return self._get_linked_mandate_ids(cr, uid, ids, 'int_mandate_ids',
                                            context=context)

    def get_linked_ext_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_ext_mandate_ids
        ==============================
        Return External Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        return self._get_linked_mandate_ids(cr, uid, ids, 'ext_mandate_ids',
                                            context=context)

    def _get_linked_mandate_ids(self, cr, uid, ids, mandate_relation,
                                context=None):
        """
        ==============================
        get_linked_mandate_ids
        ==============================
        Return State Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        mandate_categories = self.read(cr, uid, ids, [mandate_relation],
                                       context=context)
        res_ids = []
        for mandate_category in mandate_categories:
            res_ids += mandate_category[mandate_relation]
        return list(set(res_ids))

    def _check_exclusive_consistency(self, cr, uid, category_id,
                                     initial_exclu_ids, magic_categories,
                                     context=None):
        """
        Check balance between exclusive categories
        :rparam: mandate_category ids, list of initial exclusive ids,
                 list of new exclusive ids
        :rtype: Boolean
        """
        new_exclu_ids = []
        if magic_categories[0][0] == 6:
            new_exclu_ids = magic_categories[0][2]
        if magic_categories[0][0] == 4:
            new_exclu_ids = [c[1] for c in magic_categories]
            new_exclu_ids += initial_exclu_ids

        removed_ids = list(set(initial_exclu_ids) - set(new_exclu_ids))
        added_ids = list(set(new_exclu_ids) - set(initial_exclu_ids))

        if removed_ids:
            # category are not exclusives anymore
            self._impact_related_exclusive_category(cr,
                                                    uid,
                                                    category_id,
                                                    removed_ids,
                                                    'in',
                                                    context=context)
        if added_ids:
            # category are exclusives from now
            self._impact_related_exclusive_category(cr,
                                                    uid,
                                                    category_id,
                                                    added_ids,
                                                    'not in',
                                                    context=context,
                                                    exclu_ids=[category_id])

        return True

    def _impact_related_exclusive_category(self, cr, uid, category_id,
                                           linked_ids, operator, context=None,
                                           exclu_ids=None):
        """
        ==============================
        _impact_related_exclusive_category
        ==============================
        Impact relative categories to add or remove a link to current id
        """
        exclu_ids = exclu_ids or []
        for exclu_data in self.search_read(cr,
                                           uid,
                                           [('id',
                                             'in',
                                             linked_ids),
                                            ('exclusive_category_m2m_ids',
                                             operator,
                                             [category_id])],
                                           ['exclusive_category_m2m_ids'],
                                           context=context):
            exclu_ids.extend([exclu_id for exclu_id in
                              exclu_data['exclusive_category_m2m_ids']
                              if exclu_id != category_id])
            vals = dict(exclusive_category_m2m_ids=[[6, False, exclu_ids]])
            super(mandate_category, self).write(cr,
                                                uid,
                                                exclu_data['id'],
                                                vals,
                                                context=context)

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'type': fields.selection(MANDATE_CATEGORY_AVAILABLE_TYPES,
                                 'Type',
                                 select=True,
                                 required=True),
        'exclusive_category_m2m_ids': fields.many2many(
            'mandate.category',
            'mandate_category_mandate_category_rel',
            'id',
            'exclu_id',
            'Exclusive Category'),
        'sta_assembly_category_id': fields.many2one(
            'sta.assembly.category',
            string='State Assembly Category',
            track_visibility='onchange'),
        'ext_assembly_category_id': fields.many2one(
            'ext.assembly.category',
            string='External Assembly Category',
            track_visibility='onchange'),
        'int_assembly_category_id': fields.many2one(
            'int.assembly.category',
            string='Internal Assembly Category',
            track_visibility='onchange'),
        'sta_mandate_ids': fields.one2many('sta.mandate',
                                           'mandate_category_id',
                                           'State Mandates'),
        'int_mandate_ids': fields.one2many('int.mandate',
                                           'mandate_category_id',
                                           'Internal Mandates'),
        'ext_mandate_ids': fields.one2many('ext.mandate',
                                           'mandate_category_id',
                                           'External Mandates'),
        'is_submission_mandate': fields.boolean(
            string='With Wages Declaration',
            help='Submission to a Mandates and Wages Declaration'),
        'is_submission_assets': fields.boolean(
            string='With Assets Declaration',
            help='Submission to a Mandates and Assets Declaration'),
    }

    _order = 'name'

# constraints

    _sql_constraints = [
        ('ref_categ_check',
         'CHECK(sta_assembly_category_id+int_assembly_category_id+'
         'ext_assembly_category_id > 0)',
         'An Assembly Category is required.'),
    ]

    _unicity_keys = 'type, name'

# orm methods

    def copy_data(self, cr, uid, id_, default=None, context=None):
        res = super(mandate_category, self).copy_data(cr, uid, id_,
                                                      default=default,
                                                      context=context)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res

    def create(self, cr, uid, vals, context=None):
        res_id = super(mandate_category, self).create(
            cr, uid, vals, context=context)
        if 'exclusive_category_m2m_ids' in vals:
            self._check_exclusive_consistency(
                cr, uid, res_id, [], vals['exclusive_category_m2m_ids'],
                context=context)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if 'exclusive_category_m2m_ids' in vals:
            for category in self.browse(cr, uid, ids, context=context):
                cat_ids = [record.id
                           for record in category.exclusive_category_m2m_ids]
                self._check_exclusive_consistency(
                    cr, uid, category.id,
                    cat_ids, vals['exclusive_category_m2m_ids'],
                    context=context)

        res = super(mandate_category, self).write(
            cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(mandate_category, self).unlink(cr, uid, ids,
                                                   context=context)
        return res
