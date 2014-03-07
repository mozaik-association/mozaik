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

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _

"""
Available Coordinate Types:
N/A
"""
COORDINATE_AVAILABLE_TYPES = [
    ('n/a', 'N/A'),
]

coordinate_available_types = dict(COORDINATE_AVAILABLE_TYPES)

MAIN_COORDINATE_ERROR = _('Exactly one main coordinate must exist for a given partner')


class abstract_coordinate(orm.AbstractModel):

    _name = 'abstract.coordinate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _coordinate_field = None

    _columns = {
        'id': fields.integer('ID', readonly=True),

        'partner_id': fields.many2one('res.partner', 'Contact', readonly=True, required=True, select=True),
        'coordinate_category_id': fields.many2one('coordinate.category', 'Coordinate Category', select=True, track_visibility='onchange'),
        'coordinate_type': fields.selection(COORDINATE_AVAILABLE_TYPES, 'Coordinate Type'),

        'is_main': fields.boolean('Is Main', readonly=True, select=True),
        'unauthorized': fields.boolean('Unauthorized', track_visibility='onchange'),
        'vip': fields.boolean('VIP', track_visibility='onchange'),

        'is_duplicate_detected': fields.boolean('Is Duplicate Detected', track_visibility='onchange', readonly=True),
        'is_duplicate_allowed': fields.boolean('Is Duplicate Allowed', track_visibility='onchange', readonly=True),

        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),
        'active': fields.boolean('Active', readonly=True),
    }

    _rec_name = _coordinate_field

    _defaults = {
        'coordinate_type': COORDINATE_AVAILABLE_TYPES[0],
        'active': True,
    }

    _order = "partner_id, expire_date, is_main desc, coordinate_type"

# constraints

    def _check_one_main_coordinate(self, cr, uid, ids, for_unlink=False, context=None):
        """
        ==========================
        _check_one_main_coordinate
        ==========================
        Check if associated partner has exactly one main coordinate
        for a given coordinate type
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        coordinates = self.browse(cr, uid, ids, context=context)
        for coordinate in coordinates:
            if for_unlink and not coordinate.is_main:
                continue

            coordinate_ids = self.search(cr, uid, [('partner_id', '=', coordinate.partner_id.id),
                                                   ('coordinate_type', '=', coordinate.coordinate_type)], context=context)

            if for_unlink and len(coordinate_ids) > 1 and coordinate.is_main:
                return False

            if not coordinate_ids:
                continue

            coordinate_ids = self.search(cr, uid, [('partner_id', '=', coordinate.partner_id.id),
                                                   ('coordinate_type', '=', coordinate.coordinate_type),
                                                   ('is_main', '=', True)], context=context)
            if len(coordinate_ids) != 1:
                return False

        return True

    def _check_unicity(self, cr, uid, ids, context=None):
        """
        ==============
        _check_unicity
        ==============
        :rparam: False if coordinate already exists with (self._coordinate_field,partner_id,expire_date)
                 Else True
        :rtype: Boolean
        """
        coordinate = self.browse(cr, uid, ids, context=context)[0]
        res_ids = self.search(cr, uid, [('id', '!=', coordinate.id),
                                        ('partner_id', '=', coordinate.partner_id.id),
                                        (self._coordinate_field, '=', isinstance(self._columns[self._coordinate_field], fields.many2one) and coordinate[self._coordinate_field].id or coordinate[self._coordinate_field]),
                                       ], context=context)
        return len(res_ids) == 0

    _constraints = [
        (_check_unicity, _('This coordinate already exists for this contact'), ['related_field', 'partner_id', 'expire_date']),
        (_check_one_main_coordinate, MAIN_COORDINATE_ERROR, ['partner_id'])
    ]

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        ========
        name_get
        ========
        :rparam: list of tuple (id, name to display)
                 where id is the id of the object into the relation
                 and display_name, the name of this object.
        :rtype: [(id,name)] list of tuple
        """
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.read(cr, uid, ids, [self._coordinate_field], context=context):
            display_name = record[self._coordinate_field][1]
            res.append((record['id'], display_name))
        return res

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        When 'is_main' is true the coordinate has to become the main coordinate for its
        associated partner.
        :rparam: id of the new coordinate
        :rtype: integer

        **Note**
        If new coordinate is main and another main coordinate found into
        the database then the other(s) will not be main anymore
        """
        vals['coordinate_type'] = vals.get('coordinate_type') or COORDINATE_AVAILABLE_TYPES[0]
        domain_other_active_main = self.get_target_domain(vals['partner_id'], vals['coordinate_type'])
        self.user_consistency(cr, uid, vals, domain_other_active_main, context=context)
        if vals.get('is_main'):
            validate_fields = self.get_fields_to_update('validate', context)
            # assure that there are no other main coordinate of this type for this partner
            self.search_and_update(cr, uid, domain_other_active_main, validate_fields, context=context)
        new_id = super(abstract_coordinate, self).create(cr, uid, vals, context=context)
        # check new duplicate state after creation
        self.management_of_duplicate(cr, SUPERUSER_ID, [vals[self._coordinate_field]], context=context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        Objective is to manage the duplicate coordinate after the call of the super.
        """
        res = super(abstract_coordinate, self).write(cr, uid, ids, vals, context=context)
        if 'is_duplicate_detected' in vals or 'is_duplicate_allowed' in vals or self._coordinate_field in vals:
            coordinate_field_values = self.read(cr, uid, ids, [self._coordinate_field], context=context)
            if coordinate_field_values:
                field_values = []
                for coordinate_field_value in coordinate_field_values:
                    field_values.append(isinstance(coordinate_field_value[self._coordinate_field], tuple) and coordinate_field_value[self._coordinate_field][0] or coordinate_field_value[self._coordinate_field])
                self.management_of_duplicate(cr, uid, field_values, context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """
        ======
        unlink
        ======
        :rparam: True
        :rtype: boolean
        :raise: Error if the coordinate is main
                and another coordinate of the same type exists
        """
        coordinate_ids = self.search(cr, uid, [('id', 'in', ids), ('is_main', '=', False)], context=context)
        coordinate_field_values = self.read(cr, uid, ids, [self._coordinate_field], context=context)
        super(abstract_coordinate, self).unlink(cr, uid, coordinate_ids, context=context)
        coordinate_ids = list(set(ids).difference(coordinate_ids))
        if not self._check_one_main_coordinate(cr, uid, coordinate_ids, for_unlink=True, context=context):
            raise orm.except_orm(_('Error'), MAIN_COORDINATE_ERROR)
        res = super(abstract_coordinate, self).unlink(cr, uid, coordinate_ids, context=context)
        vals = []
        for val in coordinate_field_values:
            vals.append(isinstance(val[self._coordinate_field], tuple) and val[self._coordinate_field][0] or val[self._coordinate_field])
        self.management_of_duplicate(cr, uid, vals, context)
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        res = super(abstract_coordinate, self).copy_data(cr, uid, ids, default=default, context=context)
        if res.get('active', True):
            raise orm.except_orm(_('Error'), _('An active coordinate cannot be duplicated!'))
        res.update({
                    'active': True,
                    'expire_date': False,
                   })
        return res

# view methods: onchange, button

    def button_invalidate(self, cr, uid, ids, context=None):
        """
        =================
        button_invalidate
        =================
        This method invalidate a coordinate by setting
        * active to False
        * expire_date to current date
        :rparam: True
        :rtype: boolean

        **Note**
        :raise: Error if the coordinate is main
                and another coordinate of the same type exists
                (ref _check_one_main_coordinate constraint)
        """
        self.write(cr, uid, ids,
                   {'active': False,
                    'expire_date': fields.datetime.now(),
                    'is_duplicate_detected': False,
                    'is_duplicate_allowed': False,
                   }, context=context)
        return True

# public methods

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Returns partner ids linked to coordinate ids
        Path to partner must be object.partner_id
        :rparam: partner_ids
        :rtype: list of ids
        """
        model_rds = self.browse(cr, uid, ids, context=context)
        partner_ids = []
        for record in model_rds:
            partner_ids.append(record.partner_id.id)
        return partner_ids

    def set_as_main(self, cr, uid, ids, context=None):
        """
        ===========
        set_as_main
        ===========
        This method allows to switch main coordinate:
        1) Reset is_main of previous main coordinate
        2) Set is_main of new main coordinate
        :rparam: True
        :rtype: boolean
        """
        coordinate = self.browse(cr, uid, ids, context=context)[0]

        # 1) Reset is_main of previous main coordinate
        target_domain = self.get_target_domain(coordinate.partner_id.id, coordinate.coordinate_type)
        fields_to_update = self.get_fields_to_update('validate', context)
        self.search_and_update(cr, uid, target_domain, fields_to_update, context=context)

        # 2) Set is_main of new main coordinate
        res = self.write(cr, uid, ids, {'is_main': True}, context=context)

        return res

    def change_main_coordinate(self, cr, uid, partner_ids, field_id, context=None):
        """
        ========================
        change_main_coordinate
        ========================
        :param partner_ids: list of partner id
        :type partner_ids: [integer]
        :param field_id: id of the new main object selected
        :type field_id: integer
        :rparam: list of coordinate ids created
        :rtype: list of integer
        """
        return_ids = []
        for partner_id in partner_ids:
            res_ids = self.search(cr, uid, [('partner_id', '=', partner_id),
                                            (self._coordinate_field, '=', field_id)], context=context)
            if not res_ids:
                # must be create
                return_ids.append(self.create(cr, uid, {'partner_id': partner_id,
                                                        self._coordinate_field: field_id,
                                                        'is_main': True,
                                                       }, context=context))
            else:
                # If the coordinate is not already ``main``, set it as main
                if not self.read(cr, uid, res_ids[0], ['is_main'], context=context)['is_main']:
                    self.set_as_main(cr, uid, res_ids, context=context)
        return return_ids

    def search_and_update(self, cr, uid, target_domain, fields_to_update, context=None):
        """
        ==================
        search_and_update
        ==================
        :param target_domain: A domain used into a search
        :type target_domain: list of tuples
        :param fields_to_update: contain the field to be updated
        :type fields_to_update: dictionary
        :rparam: True some objects are found otherwise False
        :rparam: boolean
        **Note**
        1) Search with self on ``target_domain``
        2) Update self with ``fields_to_update``
        """
        res_ids = self.search(cr, uid, target_domain, context=context)
        save_constraints, self._constraints = self._constraints, []
        self.write(cr, uid, res_ids, fields_to_update, context=context)
        self._constraints = save_constraints
        return len(res_ids) != 0

    def management_of_duplicate(self, cr, uid, vals, context=None):
        """
        This method will update the duplicate attribute of ficep coordinate
        depending if other are found.
        :param vals: coordinate values
        :type vals: list
        """
        for v in vals:
            coordinate_ids = self.search(cr, uid, [(self._coordinate_field, '=', v)], context=context)
            if len(coordinate_ids) > 1:
                fields_to_update = None
                current_values = self.read(cr, uid, coordinate_ids, ['is_duplicate_allowed', 'is_duplicate_detected'], context=context)

                is_ok = 0
                for value in current_values:
                    if not value['is_duplicate_detected'] and value['is_duplicate_allowed']:
                        is_ok += 1
                if is_ok == 1:
                    fields_to_update = {'is_duplicate_allowed': False, 'is_duplicate_detected': False}

                is_ok = 0
                for value in current_values:
                    if not value['is_duplicate_detected'] and not value['is_duplicate_allowed']:
                        is_ok += 1
                        break
                if is_ok >= 1:
                    fields_to_update = {'is_duplicate_detected': True, 'is_duplicate_allowed': False}
            else:
                fields_to_update = {'is_duplicate_allowed': False, 'is_duplicate_detected': False}
            if fields_to_update:
                super(abstract_coordinate, self).write(cr, uid, coordinate_ids, fields_to_update, context=context)

    def get_target_domain(self, partner_id, coordinate_type):
        """
        =================
        get_target_domain
        =================
        :param partner_id: id of the partner
        :type partner_id: integer
        :parma coordinate_type: type of the coordinate
        :type coordinate_type: char
        :rparam: dictionary with ``coordinate_type`` and ``partner_id`` well set
        :rtype: dictionary
        """
        return [('partner_id', '=', partner_id),
                ('coordinate_type', '=', coordinate_type),
                ('is_main', '=', True),
               ]

    def get_fields_to_update(self, case_of, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        :param case_of: return a different dictionary depending of
                        case_of value
        :type case_of: char
        :except: raise orm_exception if invalid ``case_of``
        :rtype: dictionary
        """
        if context is None:
            context = {}

        if case_of == 'validate':
            return {'active': False,
                    'expire_date': fields.datetime.now()} if context.get('invalidate', False) else {'is_main': False}
        if case_of == 'duplicate':
            return {'is_duplicate_detected': True,
                    'is_duplicate_allowed': False}

        raise orm.except_orm(_('ERROR'), _('Invalid `case_of`'))

    def user_consistency(self, cr, uid, vals, domain_other_active_main, context=None):
        """
        :param domain_other_active_main: for research on main coordinate
        :type domain_other_active_main: list(tuples)
        :type vals: dictionary
        **Note**
        Update ``vals`` with is_main to ``True`` case of no other main coordinate found
        """
        coordinate_ids = self.search(cr, uid, domain_other_active_main, context=context)
        if not coordinate_ids:
            vals['is_main'] = True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
