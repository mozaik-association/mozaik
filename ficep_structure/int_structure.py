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
##############################################################################'''
from openerp.osv import orm, fields


class int_power_level(orm.Model):

    _name = 'int.power.level'
    _inherit = ['abstract.power.level']
    _description = 'Internal Power Level'

    _columns = {
        'assembly_category_ids': fields.one2many('int.assembly.category', 'power_level_id', 'Internal Assembly Categories', domain=[('active', '=', True)]),
        'assembly_category_inactive_ids': fields.one2many('int.assembly.category', 'power_level_id', 'Internal Assembly Categories', domain=[('active', '=', False)]),
    }

# public methods

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Power Level
        """
        alts = [
            ('', '__MIG_IPL_1'),                        # Production
            ('ficep_structure', 'int_power_level_01'),  # Test
        ]
        res = self.pool.get('ir.model.data').get_object_alternative(cr, uid, alts)[1]
        return res


class int_assembly_category(orm.Model):

    _name = 'int.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = "Internal Assembly Category"

    _columns = {
        'is_secretariat': fields.boolean("Secretariat", track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level', 'Internal Power Level', required=True, select=True, track_visibility='onchange'),
    }

    _order = 'power_level_id, name'

# constraints

    _unicity_keys = 'power_level_id, name'


class int_instance(orm.Model):

    _name = 'int.instance'
    _inherit = ['abstract.instance']
    _description = 'Internal Instance'

    _columns = {
        'parent_id': fields.many2one('int.instance', 'Parent Internal Instance', ondelete='restrict', select=True, track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level', 'Internal Power Level', required=True, select=True, track_visibility='onchange'),

        'assembly_ids': fields.one2many('int.assembly', 'instance_id', 'Internal Assemblies', domain=[('active', '=', True)]),
        'assembly_inactive_ids': fields.one2many('int.assembly', 'instance_id', 'Internal Assemblies', domain=[('active', '=', False)]),
        'electoral_district_ids': fields.one2many('electoral.district', 'int_instance_id', 'Electoral Districts', domain=[('active', '=', True)]),
        'electoral_district_inactive_ids': fields.one2many('electoral.district', 'int_instance_id', 'Electoral Districts', domain=[('active', '=', False)]),
        'multi_instance_pc_m2m_ids': fields.many2many('int.instance', 'int_instance_int_instance_rel', 'id', 'child_id',
                                                      'Multi-Instance', domain=[('active', '<=', True)]),
        'multi_instance_cp_m2m_ids': fields.many2many('int.instance', 'int_instance_int_instance_rel', 'child_id', 'id',
                                                      'Multi-Instance', domain=[('active', '<=', True)]),
    }

# public methods

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Instance
        """
        alts = [
            ('', '__MIG_II_286'),                   # Production
            ('ficep_structure', 'int_instance_01')  # Test
        ]
        res = self.pool.get('ir.model.data').get_object_alternative(cr, uid, alts)[1]
        return res


class int_assembly(orm.Model):

    _name = 'int.assembly'
    _inherit = ['abstract.assembly']
    _description = 'Internal Assembly'

    def _compute_dummy(self, cursor, uid, ids, fname, arg, context=None):
        res = {}
        assemblies = self.browse(cursor, uid, ids, context=context)
        for ass in assemblies:
            fullname = "%s (%s) " % (ass.instance_id.name, ass.assembly_category_id.name)
            res[ass.id] = fullname
            self.pool['res.partner'].write(cursor, uid, ass.partner_id.id, {'name': fullname}, context=context)
        return res

    _name_store_triggers = {
        'int.assembly': (lambda self, cr, uid, ids, context=None: ids,
                         ['instance_id', 'assembly_category_id', ], 10),
        'int.instance': (lambda self, cr, uid, ids, context=None: self.pool['int.assembly'].search(cr, uid, [('instance_id', 'in', ids)], context=context),
                         ['name', ], 10),
        'int.assembly.category': (lambda self, cr, uid, ids, context=None: self.pool['int.assembly'].search(cr, uid, [('assembly_category_id', 'in', ids)], context=context),
                                  ['name', ], 10),
    }

    _columns = {
        # dummy: define a dummy function to update the partner name associated to the assembly
        'dummy': fields.function(_compute_dummy, string="Dummy",
                                 type="char", store=_name_store_triggers,
                                 select=True),
        'assembly_category_id': fields.many2one('int.assembly.category', 'Assembly Category',
                                                select=True, required=True, track_visibility='onchange'),
        'instance_id': fields.many2one('int.instance', 'Internal Instance',
                                       select=True, required=True, track_visibility='onchange'),
        'is_designation_assembly': fields.boolean("Designation Assembly", track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one('int.assembly', string='Designation assembly',
                                                 select=True, track_visibility='onchange',
                                                 domain=[('is_designation_assembly', '=', True)]),
    }

    def create(self, cr, uid, vals, context=None):
        '''
        Produce the first value of the name field.
        Next values are generated in the function _compute_dummy
        '''
        if not vals.get('name') and not vals.get('partner_id'):
            instance = ''
            if vals.get('instance_id'):
                instance = self.pool['int.instance'].read(cr, uid, vals.get('instance_id'), ['name'], context=context)
            category = ''
            if vals.get('assembly_category_id'):
                category = self.pool['int.assembly.category'].read(cr, uid, vals.get('assembly_category_id'), ['name'], context=context)
            vals['name'] = '%s (%s)' % (instance['name'], category['name'])
        res = super(int_assembly, self).create(cr, uid, vals, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
