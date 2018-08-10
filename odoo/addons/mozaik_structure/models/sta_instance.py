# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sta_instance(orm.Model):

    _name = 'sta.instance'
    _inherit = ['abstract.instance']
    _description = 'State Instance'

    def get_linked_electoral_districts(self, cr, uid, ids, context=None):
        """
        Return electoral districts ids linked to sta_instance ids
        :rparam: sta_instance_ids
        :rtype: list of ids
        """
        sta_instances = self.read(cr, uid, ids, ['electoral_district_ids'],
                                  context=context)
        res_ids = []
        for sta_instance in sta_instances:
            res_ids += sta_instance['electoral_district_ids']
        return list(set(res_ids))

    _columns = {
        'parent_id': fields.many2one('sta.instance',
                                     'Parent State Instance',
                                     select=True,
                                     ondelete='restrict',
                                     track_visibility='onchange'),
        'secondary_parent_id': fields.many2one(
            'sta.instance',
            'Secondary Parent State Instance',
            select=True,
            track_visibility='onchange'),
        'power_level_id': fields.many2one('sta.power.level',
                                          'State Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
        'int_instance_id': fields.many2one('int.instance',
                                           'Internal Instance',
                                           required=True,
                                           select=True,
                                           track_visibility='onchange'),
        'identifier': fields.char('External Identifier (INS)',
                                  select=True,
                                  track_visibility='onchange'),
        'assembly_ids': fields.one2many('sta.assembly',
                                        'instance_id',
                                        'State Assemblies'),
        'assembly_inactive_ids': fields.one2many('sta.assembly',
                                                 'instance_id',
                                                 'State Assemblies',
                                                 domain=[
                                                     ('active', '=', False)
                                                 ]),
        'electoral_district_ids': fields.one2many('electoral.district',
                                                  'sta_instance_id',
                                                  'Electoral Districts'),
        'electoral_district_inactive_ids': fields.one2many(
            'electoral.district',
            'sta_instance_id',
            'Electoral Districts',
            domain=[
                ('active', '=', False)
            ]),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool['int.instance'].get_default(cr, uid),
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        """
        Avoid recursion in instance tree regarding secondary_parent_id field
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        uid = SUPERUSER_ID
        return orm.Model._check_recursion(self, cr, uid, ids, context=context,
                                          parent='secondary_parent_id')

    _constraints = [
        (_check_recursion, _('You can not create recursive instances'),
         ['secondary_parent_id']),
    ]

    _sql_constraints = [
        ('unique_identifier', 'UNIQUE ( identifier )',
         'The external identifier (INS) must be unique.'),
    ]
