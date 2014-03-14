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
    _description = "Internal Power Level"

    _columns = {
        'assembly_category_ids': fields.one2many('int.assembly.category', 'power_level_id',
                                                  'Internal Assembly Categories', domain=[('active', '=', True)]),
        'instance_ids': fields.one2many('int.instance', 'power_level_id', 'Internal Instances', domain=[('active', '=', True)]),
        }


class int_assembly_category(orm.Model):

    _name = 'int.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = "Internal Assembly Category"

    _columns = {
        'is_secretariat': fields.boolean("Secretariat"),
        'power_level_id': fields.many2one('int.power.level', 'Internal Power Level', required=True, ondelete='cascade'),
        'assembly_ids': fields.one2many('int.assembly', 'assembly_category_id', 'Internal Assemblies', domain=[('active', '=', True)]),
        }


class int_instance(orm.Model):

    _name = 'int.instance'
    _inherit = ['abstract.instance']
    _description = "Internal Instance"

    _columns = {
        'parent_id': fields.many2one('int.instance', 'Parent Internal Instance', select=True, ondelete='cascade', required=False),
        'child_ids': fields.one2many('int.instance', 'parent_id', string='Child Internal Instance', required=False),
        'power_level_id': fields.many2one('int.power.level', 'Internal Power Level', required=True, ondelete='cascade'),
        'assembly_ids': fields.one2many('int.assembly', 'instance_id', 'Internal Assemblies', domain=[('active', '=', True)]),
        'ext_assembly_ids': fields.one2many('ext.assembly', 'instance_id', 'External Assemblies', domain=[('active', '=', True)]),
        'sta_instance_ids': fields.one2many('sta.instance', 'id', 'State Instances', domain=[('active', '=', True)]),
        'electoral_district_ids': fields.one2many('electoral.district', 'int_instance_id', 'Electoral Districts', domain=[('active', '=', True)]),
        'multi_instance_n2m_ids': fields.many2many('int.instance',
                                        'int_instance_int_instance_rel',
                                        'id',
                                        'multi_instance_n2m_ids',
                                        'Multi-Instance'),
        }

    _order = "name"


class int_assembly(orm.Model):

    _name = 'int.assembly'
    _inherit = ['abstract.assembly']
    _description = "Internal Assembly"

    _columns = {
        'assembly_category_id': fields.many2one('int.assembly.category', 'Category',
                                                 required=True, ondelete='cascade'),
        'instance_id': fields.many2one('int.instance', 'Internal Instance',
                                                 required=True, ondelete='cascade'),
        'designation_int_power_level_id': fields.many2one('int.power.level', string='Designation Power Level',
                                                 required=True, ondelete='cascade', readonly=False),
        }
