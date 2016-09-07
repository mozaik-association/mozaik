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

from openerp import api
from openerp.osv import orm, fields
import logging

from openerp.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class int_power_level(orm.Model):

    _name = 'int.power.level'
    _inherit = ['abstract.power.level']
    _description = 'Internal Power Level'

    _columns = {
        'assembly_category_ids': fields.one2many(
            'int.assembly.category',
            'power_level_id',
            'Internal Assembly Categories',
            domain=[('active', '=', True)]
        ),
        'assembly_category_inactive_ids': fields.one2many(
            'int.assembly.category',
            'power_level_id',
            'Internal Assembly Categories',
            domain=[('active', '=', False)]
        ),
        'level_for_followers': fields.boolean('Level For Followers'),
    }

    _defaults = {
        'level_for_followers': False,
    }

# public methods

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Power Level
        """
        res_id = self.pool['ir.model.data'].xmlid_to_res_id(
            cr, SUPERUSER_ID, 'mozaik_structure.int_power_level_01')
        return res_id


class int_assembly_category(orm.Model):

    _name = 'int.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = "Internal Assembly Category"

    _columns = {
        'is_secretariat': fields.boolean("Is Secretariat",
                                         track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level',
                                          'Internal Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
    }

    _order = 'power_level_id, name'

# constraints

    _unicity_keys = 'power_level_id, name'


class int_instance(orm.Model):

    _name = 'int.instance'
    _inherit = ['abstract.instance']
    _description = 'Internal Instance'

    _columns = {
        'parent_id': fields.many2one('int.instance',
                                     'Parent Internal Instance',
                                     select=True,
                                     ondelete='restrict',
                                     track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level',
                                          'Internal Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),

        'assembly_ids': fields.one2many('int.assembly',
                                        'instance_id',
                                        'Internal Assemblies',
                                        domain=[('active', '=', True)]),
        'assembly_inactive_ids': fields.one2many('int.assembly',
                                                 'instance_id',
                                                 'Internal Assemblies',
                                                 domain=[
                                                     ('active', '=', False)
                                                 ]),
        'electoral_district_ids': fields.one2many('electoral.district',
                                                  'int_instance_id',
                                                  'Electoral Districts',
                                                  domain=[
                                                      ('active', '=', True)
                                                  ]),
        'electoral_district_inactive_ids': fields.one2many(
            'electoral.district',
            'int_instance_id',
            'Electoral Districts',
            domain=[
                ('active', '=', False)]),
        'multi_instance_pc_m2m_ids': fields.many2many(
            'int.instance',
            'int_instance_int_instance_rel',
            'id',
            'child_id',
            'Multi-Instances',
            domain=[
                ('active', '<=', True)]),
        'multi_instance_cp_m2m_ids': fields.many2many(
            'int.instance',
            'int_instance_int_instance_rel',
            'child_id',
            'id',
            'Multi-Instances',
            domain=[
                ('active', '<=', True)]),
    }

# public methods

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Power Level
        """
        res_id = self.pool['ir.model.data'].xmlid_to_res_id(
            cr, SUPERUSER_ID, 'mozaik_structure.int_instance_01')
        return res_id

    @api.multi
    def get_secretariat(self):
        '''
        Return the secretariat associated to an instance
        '''
        self.ensure_one()
        assembly_ids = self.env['int.assembly'].search([
            ('instance_id', '=', self.id), ('is_secretariat', '=', True),
        ])
        if assembly_ids:
            return assembly_ids[0]
        _logger.warning('No secretariat found for internal instance %s',
                        self.name)
        return False


class int_assembly(orm.Model):

    _name = 'int.assembly'
    _inherit = ['abstract.assembly']
    _description = 'Internal Assembly'

    _category_model = 'int.assembly.category'

    def _compute_dummy(self, cursor, uid, ids, fname, arg, context=None):
        res = {}
        assemblies = self.browse(cursor, uid, ids, context=context)
        for ass in assemblies:
            fullname = "%s (%s)" % (ass.instance_id.name,
                                    ass.assembly_category_id.name)
            res[ass.id] = fullname
            self.pool['res.partner'].write(
                cursor, uid, ass.partner_id.id,
                {'name': fullname}, context=context)
        return res

    _name_store_triggers = {
        'int.assembly': (
            lambda self, cr, uid, ids, context=None: ids, [
                'instance_id', 'assembly_category_id', ], 10),
        'int.instance': (
            lambda self, cr, uid, ids, context=None:
            self.pool['int.assembly'].search(
                cr, uid, [
                    ('instance_id', 'in', ids)], context=context), [
                'name', ], 10),
        'int.assembly.category': (
            lambda self, cr, uid, ids, context=None:
            self.pool['int.assembly'].search(
                cr, uid, [
                    ('assembly_category_id', 'in', ids)], context=context), [
                'name', ], 10),
    }

    _columns = {
        # dummy: define a dummy function to update the partner name associated
        #        to the assembly
        'dummy': fields.function(_compute_dummy,
                                 string="Dummy",
                                 type="char",
                                 store=_name_store_triggers,
                                 select=True),
        'assembly_category_id': fields.many2one(_category_model,
                                                'Assembly Category',
                                                select=True,
                                                required=True,
                                                track_visibility='onchange'),
        'instance_id': fields.many2one('int.instance',
                                       'Internal Instance',
                                       select=True,
                                       required=True,
                                       track_visibility='onchange'),
        'is_designation_assembly': fields.boolean("Is Designation Assembly",
                                                  track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly',
            string='Designation Assembly',
            select=True,
            track_visibility='onchange',
            domain=[
                ('is_designation_assembly', '=', True)
            ]),
        'is_secretariat': fields.related('assembly_category_id',
                                         'is_secretariat',
                                         string='Is Secretariat',
                                         type='boolean',
                                         relation=_category_model,
                                         store=False),
    }

# view methods: onchange, button

    def onchange_assembly_category_id(self, cr, uid, ids, assembly_category_id,
                                      context=None):
        return super(int_assembly, self).onchange_assembly_category_id(
            cr, uid, ids, assembly_category_id, context=context)

# public methods

    def get_secretariat_assembly_id(self, cr, uid, assembly_id, context=None):
        '''
        Return the secretariat related to the same instance as
        the given assembly
        '''
        instance_id = self.read(cr, uid, assembly_id, ['instance_id'],
                                context=context)['instance_id'][0]
        secretariat_id = self.pool['int.instance'].get_secretariat(
            cr, uid, [instance_id], context=context)
        return secretariat_id

    def get_followers_assemblies(self, cr, uid, int_instance_id, context=None):
        '''
        Return followers (partner) for all secretariat assemblies
        '''
        int_instance_rec = self.pool['int.instance'].browse(
            cr, uid, int_instance_id, context=context)
        int_instance_ids = []

        while int_instance_rec:
            int_instance_ids.append(int_instance_rec.id)
            int_instance_rec = int_instance_rec.parent_id

        level_for_followers_ids = self.pool['int.power.level'].search(
            cr, uid, [('level_for_followers', '=', True)], context=None)
        secretariat_categ_ids = self.pool['int.assembly.category'].search(
            cr, uid, [('is_secretariat', '=', True),
                      ('power_level_id', 'in', level_for_followers_ids)],
            context=context)
        followers_assemblies_values = self.search_read(
            cr, uid, [('instance_id', 'in', int_instance_ids),
                      ('assembly_category_id', 'in', secretariat_categ_ids)],
            ['partner_id'], context=context)
        partner_ids = []
        for followers_assemblies in followers_assemblies_values:
            partner_ids.append(followers_assemblies['partner_id'][0])

        return partner_ids
