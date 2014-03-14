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


class abstract_power_level(orm.AbstractModel):

    _name = 'abstract.power.level'
    _description = "Abstract Power Level"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'sequence': fields.integer("Sequence"),
        'name': fields.char('Name', size=128, translate=True, select=True),
        'assembly_category_ids': fields.one2many('abstract.assembly.category', 'power_level_id',
                                                  'Assembly Categories', domain=[('active', '=', True)]),
        'instance_ids': fields.one2many('abstract.instance', 'power_level_id', 'Instances', domain=[('active', '=', True)]),
        'active': fields.boolean('Active', readonly=True),
        }

    _defaults = {
        'active': True,
    }

    _order = "sequence, name"


class abstract_assembly_category(orm.AbstractModel):

    _name = 'abstract.assembly.category'
    _description = "Abstract Assembly Category"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=128, translate=True, select=True),
        'duration': fields.integer('Duration of mandate', readonly=False),
        'months_before_end_of_mandate': fields.integer('Month before end of mandate', readonly=False),
        'assembly_ids': fields.one2many('abstract.assembly', 'assembly_category_id', 'Assemblies', domain=[('active', '=', True)]),
        'active': fields.boolean('Active', readonly=True),
        }

    _defaults = {
        'active': True,
    }

    _order = "name"


class abstract_instance(orm.AbstractModel):

    _name = 'abstract.instance'
    _description = "Abstract Instance"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=128, translate=True, select=True),
        'parent_id': fields.many2one('abstract.instance', 'Parent Abstract Instance', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('abstract.instance', 'parent_id', string='Child Abstract Instance'),
        'power_level_id': fields.many2one('abstract.power.level', 'Power Level', required=True, ondelete='cascade'),
        'assembly_ids': fields.one2many('abstract.assembly', 'assembly_category_id', 'Assemblies', domain=[('active', '=', True)]),
        'active': fields.boolean('Active', readonly=True),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        }

    _defaults = {
        'active': True,
    }

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'


class abstract_assembly(orm.AbstractModel):

    _name = 'abstract.assembly'
    _description = "Abstract Assembly"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=128, translate=True, select=True, readonly=False),
        'assembly_category_id': fields.many2one('abstract.assembly.category', string='Category',
                                                 required=True, ondelete='cascade', readonly=False),
        'instance_id': fields.many2one('abstract.instance', string='Instance',
                                                 required=True, ondelete='cascade', readonly=False),
        'partner_id': fields.many2one('res.partner', 'partner_id', required=True, ondelete='cascade',
                                      context={'is_company': True, 'is_assembly': True}, readonly=False),

        'designation_int_power_level_id': fields.many2one('abstract.power.level', string='Designation Power Level',
                                                 required=True, ondelete='cascade', readonly=False),
        'months_before_end_of_mandate': fields.integer('Month before end of mandate', readonly=False),
        'active': fields.boolean('Active', readonly=True),
        }

    _defaults = {
        'active': True,
        'designation_int_power_level_id': lambda self, cr, uid, ids, context=None: self.pool.get("ir.model.data").get_object_reference(cr, uid, "ficep_structure", "int_power_level_01")[1]
    }

    _order = "name"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
