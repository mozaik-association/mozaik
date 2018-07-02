# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_coordinate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_coordinate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_coordinate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_coordinate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


# Available Coordinate Types:
# N/A
COORDINATE_AVAILABLE_TYPES = [
    ('n/a', 'N/A'),
]

coordinate_available_types = dict(COORDINATE_AVAILABLE_TYPES)

MAIN_COORDINATE_ERROR = \
    'Exactly one main coordinate must exist for a given partner'


class abstract_coordinate(orm.AbstractModel):

    _name = 'abstract.coordinate'
    _inherit = ['abstract.duplicate']
    _description = 'Abstract Coordinate'

    def _validate_vals(self, cr, uid, vals, context=None):
        """
        if no coordinate for this partner then force is_main to true
        """
        domain_other_active_main = self.get_target_domain(
            vals['partner_id'], vals['coordinate_type'])
        coordinate_ids = self.search(
            cr, uid, domain_other_active_main, context=context)
        if not coordinate_ids:
            vals['is_main'] = True
        return

    def _update_magic_numbers(self, cr, uid, magic, new_ids, context=None):
        ids = []
        if magic:
            if magic[0][0] == 4:
                ids = [magic[0][1]]
            elif magic[0][0] == 6:
                ids = magic[0][2]
        ids += new_ids
        return [(6, 0, ids)]

    def _check_force_from(self, cr, uid, email, partner_id, context=None):
        context = context or {}
        if partner_id == self.pool['res.users'].browse(
                cr, uid, uid, context=context).partner_id.id:
            context['force_from'] = email

    _discriminant_field = None

# fields

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Contact',
            readonly=True, required=True, select=True),
        'coordinate_category_id': fields.many2one(
            'coordinate.category', string='Coordinate Category',
            select=True, track_visibility='onchange'),
        'coordinate_type': fields.selection(
            COORDINATE_AVAILABLE_TYPES, 'Coordinate Type'),

        'is_main': fields.boolean('Is Main', readonly=True, select=True),
        'unauthorized': fields.boolean(
            'Unauthorized', track_visibility='onchange'),
        'vip': fields.boolean('VIP', track_visibility='onchange'),

        'bounce_counter': fields.integer(
            'Failures Counter', track_visibility='onchange'),
        'bounce_description': fields.text(
            'Last Failure Description', track_visibility='onchange'),
        'bounce_date': fields.datetime(
            'Last Failure Date', track_visibility='onchange')
    }

    _defaults = {
        'coordinate_type': COORDINATE_AVAILABLE_TYPES[0][0],
        'is_main': False,
        'unauthorized': False,
        'vip': False,
        'bounce_counter': 0,
    }

    _order = "partner_id, expire_date, is_main desc, coordinate_type"

# constraints

    def _check_one_main_coordinate(self, cr, uid, ids, for_unlink=False,
                                   context=None):
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
        uid = SUPERUSER_ID
        coordinates = self.browse(cr, uid, ids, context=context)
        for coordinate in coordinates:
            if for_unlink and not coordinate.is_main:
                continue

            coordinate_ids = self.search(
                cr, uid,
                [('partner_id', '=', coordinate.partner_id.id),
                 ('coordinate_type', '=', coordinate.coordinate_type)],
                context=context)

            if for_unlink and len(coordinate_ids) > 1 and coordinate.is_main:
                return False

            if not coordinate_ids:
                continue

            coordinate_ids = self.search(
                cr, uid,
                [('partner_id', '=', coordinate.partner_id.id),
                 ('coordinate_type', '=', coordinate.coordinate_type),
                 ('is_main', '=', True)], context=context)
            if len(coordinate_ids) != 1:
                return False

        return True

    _constraints = [
        (_check_one_main_coordinate,
         MAIN_COORDINATE_ERROR, ['partner_id', 'is_main', 'active'])
    ]

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        """
        default = default or {}
        default.update({
            'bounce_counter': 0,
            'bounce_description': False,
            'bounce_date': False,
        })
        res = super(abstract_coordinate, self).copy_data(
            cr, uid, ids, default=default, context=context)
        return res

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

        context = context or {}

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.read(
                cr, uid, ids, [self._discriminant_field,
                               'unauthorized', 'partner_id'], context=context):
            display_name = self._is_discriminant_m2o() and \
                record[self._discriminant_field][1] or \
                record[self._discriminant_field]
            if context.get('is_notification', False):
                display_name = '%s: %s' %\
                    (record['partner_id'][1], display_name)
            res.append((record['id'], display_name))
        return res

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        When 'is_main' is true the coordinate has to become
        the main coordinate for its associated partner.
        Automatically add the partner as follower of its coordinate
        :rparam: id of the new coordinate
        :rtype: integer

        **Note**
        If new coordinate is main and another main coordinate found into
        the database then the other(s) will not be main anymore
        """
        context = context or {}
        vals['coordinate_type'] = vals.get('coordinate_type') or \
            COORDINATE_AVAILABLE_TYPES[0][0]
        domain_other_active_main = self.get_target_domain(
            vals['partner_id'], vals['coordinate_type'])
        self._validate_vals(cr, uid, vals, context=context)
        if vals.get('is_main'):
            mode = context.get('invalidate') and 'deactivate' or 'secondary'
            validate_fields = self.get_fields_to_update(cr, uid, mode, context)
            # assure that there are no other main coordinate
            # of this type for this partner
            ctx = context
            if self._discriminant_field == 'email':
                ctx = context.copy()
                self._check_force_from(
                    cr, uid, vals['email'], vals['partner_id'],
                    context=ctx)
            self.search_and_update(
                cr, uid, domain_other_active_main, validate_fields,
                context=ctx)
        if self._track.get('bounce_counter'):
            # automatically add the partner as follower of its coordinate
            partner_id = vals['partner_id']
            message_follower_ids = self._update_magic_numbers(
                cr, uid, vals.get('message_follower_ids'), [partner_id],
                context=context)
            vals.update({
                'message_follower_ids': message_follower_ids,
            })
        new_id = super(abstract_coordinate, self).create(
            cr, uid, vals, context=context)
        if self._track.get('bounce_counter'):
            # do not chat with the coordinate owner
            fol_obj = self.pool['mail.followers']
            fol_ids = fol_obj.search(cr, SUPERUSER_ID, [
                ('partner_id', '=', vals['partner_id']),
                ('res_id', '=', new_id),
                ('res_model', '=', self._name),
            ], context=context)
            if fol_ids:
                imd_obj = self.pool['ir.model.data']
                _, discussion_id = imd_obj.get_object_reference(
                    cr, uid, 'mail', 'mt_comment')
                fol_obj.write(cr, SUPERUSER_ID, fol_ids, {
                    'subtype_ids': [(3, discussion_id)],
                }, context=context)
        return new_id

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
        coordinate_ids = self.search(
            cr, uid, [('id', 'in', ids),
                      ('is_main', '=', False)], context=context)
        super(abstract_coordinate, self).unlink(
            cr, uid, coordinate_ids, context=context)
        coordinate_ids = list(set(ids).difference(coordinate_ids))
        if not self._check_one_main_coordinate(
                cr, uid, coordinate_ids, for_unlink=True, context=context):
            raise orm.except_orm(_('Error'), _(MAIN_COORDINATE_ERROR))
        res = super(abstract_coordinate, self).unlink(
            cr, uid, coordinate_ids, context=context)
        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        flds = self.read(cr, uid, ids, ['active'], context=context)
        if flds.get('active', True):
            raise orm.except_orm(
                _('Error'), _('An active coordinate cannot be duplicated!'))
        res = super(abstract_coordinate, self).copy(
            cr, uid, ids, default=default, context=context)
        return res

# view methods: onchange, button

    def button_reset_counter(self, cr, uid, ids, context=None):
        """
        Reset the bounce counter
        """
        self.write(cr, uid, ids,
                   {'bounce_counter': 0}, context=context)

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
        context = context or {}
        coordinate = self.browse(cr, uid, ids, context=context)[0]

        # 1) Reset is_main of previous main coordinate
        target_domain = self.get_target_domain(
            coordinate.partner_id.id, coordinate.coordinate_type)
        mode = context.get('invalidate') and 'deactivate' or 'secondary'
        fields_to_update = self.get_fields_to_update(
            cr, uid, mode, context=context)
        ctx = context
        if self._discriminant_field == 'email':
            ctx = context.copy()
            self._check_force_from(
                cr, uid, coordinate.email, coordinate.partner_id.id,
                context=ctx)
        self.search_and_update(
            cr, uid, target_domain, fields_to_update, context=ctx)

        # 2) Set is_main of new main coordinate
        res = self.write(cr, uid, ids, {'is_main': True}, context=context)

        return res

    def change_main_coordinate(self, cr, uid, partner_ids, value,
                               context=None):
        """
        :param partner_ids: list of partner id
        :type partner_ids: [integer]
        :param value: discriminant field value
        :type value: integer or string
        :rparam: list of created coordinates
        :rtype: list of integer
        """
        return_ids = []
        for partner_id in partner_ids:
            res_ids = self.search(
                cr, uid, [('partner_id', '=', partner_id),
                          (self._discriminant_field, '=', value)],
                context=context)
            if not res_ids:
                # create it
                vals = {
                    'partner_id': partner_id,
                    self._discriminant_field: value,
                    'is_main': True,
                }
                return_ids.append(self.create(cr, uid, vals, context=context))
            else:
                # set it as main if any
                if not self.read(
                        cr, uid, res_ids[0], ['is_main'],
                        context=context)['is_main']:
                    self.set_as_main(cr, uid, res_ids, context=context)
        return return_ids

    def _validate_fields(self, cr, uid, ids, field_names, context=None):
        if context.get('no_check', False):
            return
        super(abstract_coordinate, self)._validate_fields(
            cr, uid, ids, field_names, context=context)

    def search_and_update(self, cr, uid, target_domain, fields_to_update,
                          context=None):
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
        if res_ids:
            ctx = context.copy()
            ctx.update({'no_check': True})
            self.write(cr, uid, res_ids, fields_to_update, context=ctx)
        return len(res_ids) != 0

    def get_target_domain(self, partner_id, coordinate_type):
        """
        =================
        get_target_domain
        =================
        :param partner_id: id of the partner
        :type partner_id: integer
        :parma coordinate_type: type of the coordinate
        :type coordinate_type: char
        :rparam: dictionary with ``coordinate_type`` and ``partner_id`` well
        set
        :rtype: dictionary
        """
        return [
            ('partner_id', '=', partner_id),
            ('coordinate_type', '=', coordinate_type),
            ('is_main', '=', True),
        ]

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        :param mode: return a dictionary depending on mode value
        :type mode: char
        """
        res = super(abstract_coordinate, self).get_fields_to_update(
            cr, uid, mode, context=context)
        if mode == 'main':
            res.update({
                'is_main': True,
            })
        if mode == 'secondary':
            res.update({
                'is_main': False,
            })
        return res

    def ensure_one_main_coordinate(self, cr, uid, ids, invalidate=False,
                                   vals=False, context=None):
        '''
            This method ensure that a main coordinate will remain after
            an action
        '''
        context = context.copy() or {}
        limit = 1 if not invalidate else False
        rejected_ids = []
        for coordinate in self.browse(cr, uid, ids, context=context):
            if invalidate:
                domain = ('id', 'not in', ids)
            else:
                domain = ('id', '!=', coordinate.id)
            coord_ids = self.search(
                cr, uid, [('partner_id', '=', coordinate.partner_id.id),
                          ('coordinate_type', '=', coordinate.coordinate_type),
                          domain], limit=limit, context=context)
            if coordinate.is_main and len(coord_ids) == 1:
                new_main = self.browse(cr, uid, coord_ids[0], context=context)
                context['invalidate'] = invalidate
                coordinate_field = self._discriminant_field
                coordinate_value = self._is_discriminant_m2o() and \
                    new_main[coordinate_field].id or \
                    new_main[coordinate_field]
                self.change_main_coordinate(
                    cr, uid, [coordinate.partner_id.id],
                    coordinate_value, context=context)
                if vals:
                    self.write(cr, uid, coordinate.id, vals, context=context)
            else:
                rejected_ids.append(coordinate.id)
        return rejected_ids

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        context = context.copy() if context else {}
        rejected_ids = self.ensure_one_main_coordinate(
            cr, uid, ids, invalidate=True, context=context)
        return super(abstract_coordinate, self).action_invalidate(
            cr, uid, rejected_ids, context=context, vals=vals)
