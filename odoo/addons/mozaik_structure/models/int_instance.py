# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api
from openerp.osv import orm, fields
import logging

from openerp.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)


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
