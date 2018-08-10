# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sta_assembly(orm.Model):

    _name = 'sta.assembly'
    _inherit = ['abstract.assembly']
    _description = 'State Assembly'

    def _compute_dummy(self, cursor, uid, ids, fname, arg, context=None):
        res = {}
        assemblies = self.browse(cursor, uid, ids, context=context)
        for ass in assemblies:
            fullname = '%s (%s)' % (ass.instance_id.name,
                                    ass.assembly_category_id.name)
            res[ass.id] = fullname
            self.pool['res.partner'].write(cursor, uid, ass.partner_id.id,
                                           {'name': fullname}, context=context)
        return res

    _name_store_triggers = {
        'sta.assembly': (
            lambda self, cr, uid, ids, context=None: ids, [
                'instance_id', 'assembly_category_id', ], 10),
        'sta.instance': (
            lambda self, cr, uid, ids, context=None:
            self.pool['sta.assembly'].search(
                cr, uid, [
                    ('instance_id', 'in', ids)], context=context), [
                'name', ], 10),
        'sta.assembly.category': (
            lambda self, cr, uid, ids, context=None:
            self.pool['sta.assembly'].search(
                cr, uid, [
                    ('assembly_category_id', 'in', ids)], context=context), [
                'name', ], 10),
    }

    _columns = {
        # dummy: define a dummy function to update the partner name associated
        #        to the assembly
        'dummy': fields.function(_compute_dummy,
                                 string='Dummy',
                                 type='char',
                                 store=_name_store_triggers,
                                 select=True),
        'assembly_category_id': fields.many2one('sta.assembly.category',
                                                'Assembly Category',
                                                select=True,
                                                required=True,
                                                track_visibility='onchange'),
        'instance_id': fields.many2one('sta.instance',
                                       'State Instance',
                                       select=True,
                                       required=True,
                                       track_visibility='onchange'),
        'is_legislative': fields.related('assembly_category_id',
                                         'is_legislative',
                                         string='Is Legislative',
                                         type='boolean',
                                         relation='sta.assembly.category',
                                         store=False),
        'electoral_district_ids': fields.one2many(
            'electoral.district', 'assembly_id',
            string='Abstract Candidatures',
            domain=[('active', '<=', True)]),
    }
