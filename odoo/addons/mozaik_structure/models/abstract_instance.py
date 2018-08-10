# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


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

    _constraints = [
        (orm.Model._check_recursion,
         _('You can not create recursive instances'), ['parent_id']),
    ]

    _unicity_keys = 'power_level_id, name'

    def name_get(self, cr, uid, ids, context=None):
        """
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
