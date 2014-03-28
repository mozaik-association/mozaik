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


class partner_relation(orm.Model):

    _name = 'partner.relation'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'subject_partner_id': fields.many2one('res.partner', string='Subject Relation', required=True, select=True, track_visibility='onchange'),
        'object_partner_id': fields.many2one('res.partner', string='Object Relation', required=True, select=True, track_visibility='onchange'),
        'partner_relation_category_id': fields.many2one('partner.relation.category', string='Partner Relation Category', required=True, select=True, track_visibility='onchange'),

        # phone coordinate
        'fix_coordinate_id': fields.many2one('phone.coordinate', string='Fix Coordinate', select=True, track_visibility='onchange'),
        'mobile_coordinate_id': fields.many2one('phone.coordinate', string='Mobile Coordinate', select=True, track_visibility='onchange'),
        'fax_coordinate_id': fields.many2one('phone.coordinate', string='Fax Coordinate', select=True, track_visibility='onchange'),

        # address coordinate
        'postal_coordinate_id': fields.many2one('postal.coordinate', string='Postal Coordinate', select=True, track_visibility='onchange'),
        # email coordinate
        'email_coordinate_id': fields.many2one('email.coordinate', string='Email Coordinate', select=True, track_visibility='onchange'),
    }

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
        (_check_relation_qualification, _('Error! A Relation Must Be Declared Between Two Different Contact And Must Exist In Only One Way'),
                                       ['subject_partner_id', 'object_partner_id', 'partner_relation_category_id']),
    ]


class partner_relation_category(orm.Model):

    _name = 'partner.relation.category'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'subject_name': fields.char('Subject', required=True, select=True, track_visibility='onchange'),
        'object_name': fields.char('Object', required=True, select=True, track_visibility='onchange'),
    }

    _rec_name = "subject_name"

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

        **Notes**
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
