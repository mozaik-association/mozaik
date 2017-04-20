# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_structure, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_structure is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_structure is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_structure.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


class abstract_power_level(orm.AbstractModel):

    _name = 'abstract.power.level'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Power Level'

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'sequence': fields.integer('Sequence',
                                   required=True,
                                   track_visibility='onchange',
                                   group_operator='min'),
        'assembly_category_ids': fields.one2many(
            'abstract.assembly.category',
            'power_level_id',
            'Assembly Categories',
            domain=[('active', '=', True)]),
        'assembly_category_inactive_ids': fields.one2many(
            'abstract.assembly.category',
            'power_level_id',
            'Assembly Categories',
            domain=[('active', '=', False)]),
    }

    _order = 'sequence, name'

    _defaults = {
        'sequence': 5,
    }

# constraints

    _unicity_keys = 'name'


class abstract_assembly_category(orm.AbstractModel):

    _name = 'abstract.assembly.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Assembly Category'

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'duration': fields.integer('Duration of Mandates',
                                   track_visibility='onchange'),
        'months_before_end_of_mandate': fields.integer(
            'Alert Delay (#Months)',
            track_visibility='onchange', group_operator='min'),
        'power_level_id': fields.many2one('abstract.power.level',
                                          'Power Level'),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'name'


class abstract_instance(orm.AbstractModel):

    _name = 'abstract.instance'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Instance'

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
            track_visibility='onchange'),
        'power_level_id': fields.many2one(
            'abstract.power.level',
            'Power Level',
            required=True,
            select=True,
            track_visibility='onchange'),
        'parent_id': fields.many2one(
            'abstract.instance',
            'Parent Instance',
            select=True,
            track_visibility='onchange'),
        'parent_left': fields.integer(
            'Left Parent',
            select=True),
        'parent_right': fields.integer(
            'Right Parent',
            select=True),
        'assembly_ids': fields.one2many(
            'abstract.assembly',
            'assembly_category_id',
            'Assemblies',
            domain=[
                ('active',
                 '=',
                 True)]),
        'assembly_inactive_ids': fields.one2many(
            'abstract.assembly',
            'assembly_category_id',
            'Assemblies',
            domain=[
                ('active',
                 '=',
                 False)]),
    }

    _parent_name = 'parent_id'
    _parent_store = True
    _parent_order = 'name'
    _order = 'name'

# constraints

    _constraints = [
        (orm.Model._check_recursion,
         _('You can not create recursive instances'), ['parent_id']),
    ]

    _unicity_keys = 'power_level_id, name'

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
        uid = SUPERUSER_ID
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.read(cr, uid, ids, ['name', 'power_level_id'],
                                context=context):
            display_name = '%s (%s)' % \
                           (record['name'], record['power_level_id'][1])
            res.append((record['id'], display_name))
        return res


class abstract_assembly(orm.AbstractModel):

    _name = 'abstract.assembly'
    _inherit = ['mozaik.abstract.model']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _description = 'Abstract Assembly'

    _category_model = 'abstract.assembly.category'

    def _build_name(self, cr, uid, vals, context=None):
        '''
        Build the name of the related partner
        '''
        kind = self._name[:3]
        if kind == 'ext':
            model = 'res.partner'
            field = 'ref_partner_id'
        else:
            model = '%s.instance' % kind
            field = 'instance_id'
        if not vals.get(field) or \
                not vals.get('assembly_category_id'):
            return False
        instance = self.pool[model].read(
            cr, uid, vals.get(field), ['name'], context=context)
        category = self.pool['%s.assembly.category' % kind].read(
            cr, uid, vals.get('assembly_category_id'), ['name'],
            context=context)
        name = '%s (%s)' % (instance['name'], category['name'])
        return name

    _columns = {
        'assembly_category_id': fields.many2one(
            _category_model,
            string='Category',
            select=True,
            required=True,
            track_visibility='onchange'),
        'instance_id': fields.many2one(
            'abstract.instance',
            string='Instance',
            select=True,
            required=True,
            track_visibility='onchange'),
        'partner_id': fields.many2one(
            'res.partner',
            string='Associated Partner',
            select=True,
            required=True,
            ondelete='restrict', auto_join=True),
        'months_before_end_of_mandate': fields.integer(
            'Alert Delay (#Months)',
            track_visibility='onchange', group_operator='min'),
    }

    _defaults = {
        'is_company': True,
        'is_assembly': True,
    }

    _order = 'partner_id, assembly_category_id'

# constraints

    def _check_consistent_power_level(self, cr, uid, ids, context=None):
        """
        =============================
        _check_consistent_power_level
        =============================
        Check if power levels of assembly category and instance are
        consistents.
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        Note:
        Only relevant for internal and state assemblies
        """
        uid = SUPERUSER_ID
        assemblies = self.browse(cr, uid, ids, context=context)
        for assembly in assemblies:
            if not assembly.assembly_category_id._model._columns.\
                    get('power_level_id'):
                break
            if assembly.assembly_category_id.power_level_id and \
               assembly.assembly_category_id.power_level_id.id !=\
               assembly.instance_id.power_level_id.id:
                return False

        return True

    _constraints = [
        (_check_consistent_power_level,
         _('Power level of category and instance are inconsistent'),
         ['assembly_category_id', 'instance_id'])
    ]

    _unicity_keys = 'instance_id, assembly_category_id'

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        Produce the first value of the name field.
        Next values are generated by the function _compute_dummy
        '''
        if not vals.get('name') and not vals.get('partner_id'):
            vals['name'] = self._build_name(cr, uid, vals, context=context)
        res = super(abstract_assembly, self).create(
            cr, uid, vals, context=context)
        return res

# view methods: onchange, button

    def onchange_assembly_category_id(self, cr, uid, ids, assembly_category_id,
                                      context=None):
        res = {}
        res['value'] = dict(months_before_end_of_mandate=False)
        if assembly_category_id:
            assembly_category = self.pool.get(self._category_model).browse(
                cr, uid, assembly_category_id)
            value = assembly_category.months_before_end_of_mandate
            res['value'] = dict(months_before_end_of_mandate=value)

        return res
