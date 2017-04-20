# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_person_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_person_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_person_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_person_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


class partner_relation_category(orm.Model):

    _name = 'partner.relation.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partners Relation Category'

    _columns = {
        'subject_name': fields.char(
            'Subject Relation Name',
            required=True,
            select=True,
            track_visibility='onchange'),
        'object_name': fields.char(
            'Object Relation Name',
            required=True,
            select=True,
            track_visibility='onchange'),
    }

    _rec_name = 'subject_name'

# constraints

    _unicity_keys = 'subject_name'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        ========
        name_get
        ========
        :type context: dictionary
        :param context: may contains key ``object``
        :rtype: list(tuple)
        :param: list that contains for all id in ids, the corresponding name

        *Notes*
        if object is false of not present into the context:
            super is calling
        else:
            the name_get will be ``object_name``
        """
        if context is None:
            context = {}
        res = []
        if context.get('object', False):
            for record in self.browse(cr, uid, ids, context=context):
                res.append((record.id, record.object_name))
        else:
            res = super(
                partner_relation_category,
                self).name_get(
                cr,
                uid,
                ids,
                context=context)
        return res

    def name_search(
            self,
            cr,
            uid,
            name,
            args=None,
            operator='ilike',
            context=None,
            limit=100):
        args = args or []
        if context.get('object', False):
            if name:
                ids = self.search(
                    cr, uid, [
                        ('object_name', operator, name)], context=context)
            else:
                ids = self.search(cr, uid, args, limit=limit, context=context)
            res = self.name_get(cr, uid, ids, context)
        else:
            res = super(
                partner_relation_category,
                self).name_search(
                cr,
                uid,
                name,
                args=args,
                operator=operator,
                context=context,
                limit=limit)
        return res


class partner_relation(orm.Model):

    _name = 'partner.relation'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partners Relation'

    _columns = {
        'subject_partner_id': fields.many2one(
            'res.partner', string='Subject', required=True, select=True,
            track_visibility='onchange'),
        'object_partner_id': fields.many2one(
            'res.partner', string='Object', required=True, select=True,
            track_visibility='onchange'),
        'partner_relation_category_id': fields.many2one(
            'partner.relation.category', string='Relation Category',
            required=True, select=True, track_visibility='onchange'),
        'note': fields.text('Notes', track_visibility='onchange'),
        'date_from': fields.date('From', track_visibility='onchange'),
        'date_to': fields.date('To', track_visibility='onchange'),

        # coordinates
        'email_coordinate_id': fields.many2one(
            'email.coordinate', string='Email Coordinate', select=True,
            track_visibility='onchange'),
        'postal_coordinate_id': fields.many2one(
            'postal.coordinate', string='Postal Coordinate', select=True,
            track_visibility='onchange'),
        'fix_coordinate_id': fields.many2one(
            'phone.coordinate', string='Fix Coordinate', select=True,
            track_visibility='onchange'),
        'mobile_coordinate_id': fields.many2one(
            'phone.coordinate', string='Mobile Coordinate', select=True,
            track_visibility='onchange'),
        'fax_coordinate_id': fields.many2one(
            'phone.coordinate', string='Fax Coordinate', select=True,
            track_visibility='onchange'),
    }

    _rec_name = 'partner_relation_category_id'

# constraints

    def _check_relation_qualification(self, cr, uid, ids, context=None):
        """
        =============================
        _check_relation_qualification
        =============================
        :rparam: False if object_partner_id is equals to subject_partner_id
                 Else True
        :rtype: Boolean
        """
        uid = SUPERUSER_ID
        partner_relations = self.browse(cr, uid, ids, context=context)
        for partner_relation in partner_relations:
            partner_id = partner_relation.object_partner_id.id
            if partner_relation.subject_partner_id.id == partner_id:
                return False
            if self.search(
                    cr, uid,
                    [('subject_partner_id',
                      '=',
                      partner_relation.object_partner_id.id),
                     ('object_partner_id',
                      '=',
                      partner_relation.subject_partner_id.id),
                     ('partner_relation_category_id',
                      '=',
                      partner_relation.partner_relation_category_id.id)],
                    context=context):
                return False
        return True

    _constraints = [
        (_check_relation_qualification,
         _('A relation must associate two contacts and must exist in only '
           'one way!'),
            [
             'subject_partner_id',
             'object_partner_id',
             'partner_relation_category_id']),
    ]

    _unicity_keys = 'subject_partner_id, partner_relation_category_id, ' + \
        'object_partner_id'

    _sql_constraints = [
        ('date_check',
         "CHECK((date_from <= date_to or date_to is null) or " +
         "(date_from is null and date_to is null))",
         "The start date must be anterior to the end date."),
    ]

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        if context.get('object', False):
            for record in self.browse(cr, uid, ids, context=context):
                res.append((record.id, record.object_partner_id.display_name))
        else:
            for record in self.browse(cr, uid, ids, context=context):
                res.append((record.id, record.subject_partner_id.display_name))
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        flds = self.read(cr, uid, ids, ['active'], context=context)
        if flds.get('active', True):
            raise orm.except_orm(
                _('Error'),
                _('An active relation cannot be duplicated!'))
        res = super(
            partner_relation,
            self).copy(
            cr,
            uid,
            ids,
            default=default,
            context=context)
        return res

# public methods

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        Invalidates relations at the current date
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        date_to = vals.get('date_to') or fields.date.today()
        for rel in self.browse(cr, uid, ids, context=context):
            if rel.date_to and date_to >= rel.date_to:
                date_to = rel.date_to
            if not rel.date_from:
                date_to = False
            elif date_to <= rel.date_from:
                date_to = rel.date_from

            vals = {'date_to': date_to}

            if rel.date_from > fields.date.today():
                vals = {'date_to': False, 'date_from': False}

            super(partner_relation, self).action_invalidate(
                cr, uid, [rel.id],
                context=context, vals=vals)

        return True
