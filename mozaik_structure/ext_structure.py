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


class ext_assembly_category(orm.Model):

    _name = 'ext.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = 'External Assembly Category'

    _columns = {
        # Unused field
        'power_level_id': fields.many2one('int.power.level',
                                          'Internal Power Level'),
    }


class ext_assembly(orm.Model):

    _name = 'ext.assembly'
    _inherit = ['abstract.assembly']
    _description = "External Assembly"

    _category_model = 'ext.assembly.category'

    def _compute_dummy(self, cursor, uid, ids, fname, arg, context=None):
        res = {}
        assemblies = self.browse(cursor, uid, ids, context=context)
        for ass in assemblies:
            fullname = "%s (%s)" % (ass.ref_partner_id.name,
                                    ass.assembly_category_id.name)
            res[ass.id] = fullname
            self.pool['res.partner'].write(cursor, uid, ass.partner_id.id,
                                           {'name': fullname}, context=context)
        return res

    _name_store_triggers = {
        'ext.assembly': (
            lambda self, cr, uid, ids, context=None: ids, [
                'ref_partner_id', 'assembly_category_id', ], 10),
        'res.partner': (
            lambda self, cr, uid, ids, context=None:
            self.pool['ext.assembly'].search(
                cr, uid, [
                    ('ref_partner_id', 'in', ids)], context=context), [
                'lastname', ], 10),
        'ext.assembly.category': (
            lambda self, cr, uid, ids, context=None:
            self.pool['ext.assembly'].search(
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
        'designation_int_assembly_id': fields.many2one(
            'int.assembly',
            string='Designation Assembly',
            select=True,
            track_visibility='onchange',
            domain=[
                ('is_designation_assembly', '=', True)
            ]),
        'ref_partner_id': fields.many2one('res.partner',
                                          string='Legal Person',
                                          select=True,
                                          required=True,
                                          ondelete='restrict',
                                          track_visibility='onchange'),
    }

    _defaults = {
        'instance_id': lambda self, cr, uid, ids, context=None:
        self.pool.get('int.instance').get_default(cr, uid)
    }

# constraints

    _unicity_keys = 'ref_partner_id, assembly_category_id'

# view methods: onchange, button

    def onchange_assembly_category_id(self, cr, uid, ids, assembly_category_id,
                                      context=None):
        return super(ext_assembly, self).onchange_assembly_category_id(
            cr, uid, ids, assembly_category_id, context=context)
