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


class partner_relation_category(orm.Model):

    _name = 'partner.relation.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partners Relation Category'

    _columns = {
        'subject_name': fields.char('Subject Relation Name', required=True, select=True, track_visibility='onchange'),
        'object_name': fields.char('Object Relation Name', required=True, select=True, track_visibility='onchange'),
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
            res = super(partner_relation_category, self).name_get(cr, uid, ids, context=context)
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        if context.get('object', False):
            if name:
                ids = self.search(cr, uid, [('object_name', operator, name)], context=context)
            else:
                ids = self.search(cr, uid, args, limit=limit, context=context)
            res = self.name_get(cr, uid, ids, context)
        else:
            res = super(partner_relation_category, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)
        return res


class partner_relation(orm.Model):

    _name = 'partner.relation'
    _inherit = ['mozaik.abstract.model']
    _description = 'Partners Relation'

    _columns = {
        'subject_partner_id': fields.many2one('res.partner', string='Subject', required=True, select=True, track_visibility='onchange'),
        'object_partner_id': fields.many2one('res.partner', string='Object', required=True, select=True, track_visibility='onchange'),
        'partner_relation_category_id': fields.many2one('partner.relation.category', string='Relation Category', required=True, select=True, track_visibility='onchange'),
        'note': fields.text('Notes', track_visibility='onchange'),
        'date_from': fields.date('From', track_visibility='onchange'),
        'date_to': fields.date('To', track_visibility='onchange'),

        # coordinates
        'email_coordinate_id': fields.many2one('email.coordinate', string='Email Coordinate', select=True, track_visibility='onchange'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', string='Postal Coordinate', select=True, track_visibility='onchange'),
        'fix_coordinate_id': fields.many2one('phone.coordinate', string='Fix Coordinate', select=True, track_visibility='onchange'),
        'mobile_coordinate_id': fields.many2one('phone.coordinate', string='Mobile Coordinate', select=True, track_visibility='onchange'),
        'fax_coordinate_id': fields.many2one('phone.coordinate', string='Fax Coordinate', select=True, track_visibility='onchange'),
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
        partner_relations = self.browse(cr, uid, ids, context=context)
        for partner_relation in partner_relations:
            if partner_relation.subject_partner_id.id == partner_relation.object_partner_id.id:
                return False
            if self.search(cr, uid, [('subject_partner_id', '=', partner_relation.object_partner_id.id),
                                     ('object_partner_id', '=', partner_relation.subject_partner_id.id),
                                     ('partner_relation_category_id', '=', partner_relation.partner_relation_category_id.id)], context=context):
                return False
        return True

    _constraints = [
        (_check_relation_qualification, _('A relation must associate two contacts and must exist in only one way!'),
                                       ['subject_partner_id', 'object_partner_id', 'partner_relation_category_id']),
    ]

    _unicity_keys = 'subject_partner_id, partner_relation_category_id, object_partner_id'

    _sql_constraints = [
        ('date_check', "CHECK((date_from <= date_to or date_to is null) or (date_from is null and date_to is null))",
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
            raise orm.except_orm(_('Error'), _('An active relation cannot be duplicated!'))
        res = super(partner_relation, self).copy(cr, uid, ids, default=default, context=context)
        return res
