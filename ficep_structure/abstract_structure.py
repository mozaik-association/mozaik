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


class abstract_power_level(orm.AbstractModel):

    _name = 'abstract.power.level'
    _description = "Abstract Power Level"
    _inherit = ['abstract.ficep.model']

    _columns = {
        'sequence': fields.integer("Sequence", required=True, track_visibility='onchange'),
        'name': fields.char('Name', size=128, translate=True, select=True, required=True, track_visibility='onchange'),
        'assembly_category_ids': fields.one2many('abstract.assembly.category', 'power_level_id', 'Assembly Categories'),
        'assembly_category_inactive_ids': fields.one2many('abstract.assembly.category', 'power_level_id', 'Assembly Categories', domain=[('active', '=', False)]),
    }

    _defaults = {
        'sequence': 5,
    }

    _order = "sequence, name"


class abstract_assembly_category(orm.AbstractModel):

    _name = 'abstract.assembly.category'
    _description = "Abstract Assembly Category"
    _inherit = ['abstract.ficep.model']

    _columns = {
        'name': fields.char('Name', size=128, select=True, required=True, track_visibility='onchange'),
        'duration': fields.integer('Duration of mandates', track_visibility='onchange'),
        'months_before_end_of_mandate': fields.integer('Months before end of mandate', track_visibility='onchange'),
    }

    _order = "name"


class abstract_instance(orm.AbstractModel):

    _name = 'abstract.instance'
    _description = "Abstract Instance"
    _inherit = ['abstract.ficep.model']

    _columns = {
        'name': fields.char('Name', size=128, select=True, required=True, track_visibility='onchange'),
        'parent_id': fields.many2one('abstract.instance', 'Parent Abstract Instance', select=True, track_visibility='onchange'),
        'power_level_id': fields.many2one('abstract.power.level', 'Power Level', required=True, track_visibility='onchange'),
        'assembly_ids': fields.one2many('abstract.assembly', 'assembly_category_id', 'Assemblies'),
        'assembly_inactive_ids': fields.one2many('abstract.assembly', 'assembly_category_id', 'Assemblies', domain=[('active', '=', False)]),
        'parent_left': fields.integer('Left Parent', select=True),
        'parent_right': fields.integer('Right Parent', select=True),
    }

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

# constraints

    _constraints = [
        (orm.Model._check_recursion, _('Error ! You can not create recursive instances'), ['parent_id']),
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
        for record in self.read(cr, uid, ids, ['name', 'power_level_id'], context=context):
            display_name = '%s (%s)' % (record['name'], record['power_level_id'][1])
            res.append((record['id'], display_name))
        return res


class abstract_assembly(orm.AbstractModel):

    _name = 'abstract.assembly'
    _description = "Abstract Assembly"
    _inherit = ['abstract.ficep.model']
    _inherits = {
        'res.partner': 'partner_id',
    }

    _columns = {
        'assembly_category_id': fields.many2one('abstract.assembly.category', string='Category',
                                                 required=True, track_visibility='onchange'),
        'instance_id': fields.many2one('abstract.instance', string='Instance',
                                                 required=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Associated Partner', required=True, ondelete='cascade',
                                      context={'is_company': True, 'is_assembly': True}),
        'designation_int_power_level_id': fields.many2one('abstract.power.level', string='Designation Power Level',
                                                 required=True, track_visibility='onchange'),
        'months_before_end_of_mandate': fields.integer('Months before end of mandate', track_visibility='onchange'),
    }

    _defaults = {
        'is_company': True,
        'is_assembly': True,
        'designation_int_power_level_id': lambda self, cr, uid, ids, context=None: self.pool.get("ir.model.data").get_object_reference(cr, uid, "ficep_structure", "int_power_level_01")[1]
    }

# constraints

    def _check_consistent_power_level(self, cr, uid, ids, context=None):
        """
        =============================
        _check_consistent_power_level
        =============================
        Check if power levels of assembly category and instance are consistents.
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        Note:
        Only relevant for internal and state assemblies
        """
        assemblies = self.browse(cr, uid, ids, context=context)
        for assembly in assemblies:
            if not assembly.assembly_category_id._model._columns.get('power_level_id'):
                break
            if assembly.assembly_category_id.power_level_id.id != assembly.instance_id.power_level_id.id:
                return False

        return True

    _constraints = [
        (_check_consistent_power_level, _('Power level of category and power level of instance are inconsistents'),
          ['assembly_category_id', 'instance_id'])
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
