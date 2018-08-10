# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class electoral_district(orm.Model):

    _name = 'electoral.district'
    _inherit = ['mozaik.abstract.model']
    _description = 'Electoral District'

    _instance_store_dict = {
        'electoral.district': (lambda self, cr, uid, ids, context=None:
                               ids, ['sta_instance_id'], 10),
        'sta.instance': (sta_instance.get_linked_electoral_districts,
                         ['int_instance_id'], 20),
    }
    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'sta_instance_id': fields.many2one('sta.instance',
                                           'State Instance',
                                           required=True,
                                           select=True,
                                           track_visibility='onchange'),
        'int_instance_id': fields.related('sta_instance_id',
                                          'int_instance_id',
                                          string='Internal Instance',
                                          select=True,
                                          type='many2one',
                                          relation="int.instance",
                                          store=_instance_store_dict,
                                          ),
        'assembly_id': fields.many2one('sta.assembly',
                                       'Assembly',
                                       required=True,
                                       select=True,
                                       track_visibility='onchange',
                                       domain=[('is_legislative', '=', True)]),
        'power_level_id': fields.related('assembly_id',
                                         'assembly_category_id',
                                         'power_level_id',
                                         string='Power Level',
                                         type='many2one',
                                         relation='sta.power.level'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly',
            string='Designation Assembly',
            required=True,
            select=True,
            track_visibility='onchange',
            domain=[
                ('is_designation_assembly', '=', True)
            ]),
        'assembly_category_id': fields.related(
            'assembly_id',
            'assembly_category_id',
            string='State Assembly Category',
            type='many2one',
            relation='sta.assembly.category'),
    }

    _sql_constraints = [
        ('unique_name', 'UNIQUE ( name )',
         'The name must be unique.'),
    ]

    _unicity_keys = 'sta_instance_id, assembly_id'

    def onchange_sta_instance_id(self, cr, uid, ids, sta_instance_id,
                                 context=None):
        return {
            'value': {
                'name': sta_instance_id and
                self.pool.get('sta.instance').name_get(
                    cr, uid, sta_instance_id, context=context)[0][1] or False,
                'int_instance_id': sta_instance_id and
                self.pool.get('sta.instance').read(
                    cr, uid, sta_instance_id, ['int_instance_id'],
                    context=context)['int_instance_id'] or False,
            }
        }
