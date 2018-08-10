# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api
from openerp.osv import orm, fields


class int_assembly(orm.Model):

    _name = 'int.assembly'
    _inherit = ['abstract.assembly']
    _description = 'Internal Assembly'

    _category_model = 'int.assembly.category'

    def _compute_dummy(self, cursor, uid, ids, fname, arg, context=None):
        res = {}
        assemblies = self.browse(cursor, uid, ids, context=context)
        for ass in assemblies:
            fullname = "%s (%s)" % (ass.instance_id.name,
                                    ass.assembly_category_id.name)
            res[ass.id] = fullname
            self.pool['res.partner'].write(
                cursor, uid, ass.partner_id.id,
                {'name': fullname}, context=context)
        return res

    _name_store_triggers = {
        'int.assembly': (
            lambda self, cr, uid, ids, context=None: ids, [
                'instance_id', 'assembly_category_id', ], 10),
        'int.instance': (
            lambda self, cr, uid, ids, context=None:
            self.pool['int.assembly'].search(
                cr, uid, [
                    ('instance_id', 'in', ids)], context=context), [
                'name', ], 10),
        'int.assembly.category': (
            lambda self, cr, uid, ids, context=None:
            self.pool['int.assembly'].search(
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
        'is_designation_assembly': fields.boolean("Is Designation Assembly",
                                                  track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly',
            string='Designation Assembly',
            select=True,
            track_visibility='onchange',
            domain=[
                ('is_designation_assembly', '=', True)
            ]),
        'is_secretariat': fields.related('assembly_category_id',
                                         'is_secretariat',
                                         string='Is Secretariat',
                                         type='boolean',
                                         relation=_category_model,
                                         store=False),
    }

    def onchange_assembly_category_id(self, cr, uid, ids, assembly_category_id,
                                      context=None):
        return super(int_assembly, self).onchange_assembly_category_id(
            cr, uid, ids, assembly_category_id, context=context)

    def get_secretariat_assembly_id(self, cr, uid, assembly_id, context=None):
        '''
        Return the secretariat related to the same instance as
        the given assembly
        '''
        instance_id = self.read(cr, uid, [assembly_id], ['instance_id'],
                                context=context)[0]['instance_id'][0]
        secretariat_id = self.pool['int.instance'].get_secretariat(
            cr, uid, [instance_id], context=context)
        return secretariat_id

    def get_followers_assemblies(self, cr, uid, int_instance_id, context=None):
        '''
        Return followers (partner) for all secretariat assemblies
        '''
        int_instance_rec = self.pool['int.instance'].browse(
            cr, uid, int_instance_id, context=context)
        int_instance_ids = []

        while int_instance_rec:
            int_instance_ids.append(int_instance_rec.id)
            int_instance_rec = int_instance_rec.parent_id

        level_for_followers_ids = self.pool['int.power.level'].search(
            cr, uid, [('level_for_followers', '=', True)], context=None)
        secretariat_categ_ids = self.pool['int.assembly.category'].search(
            cr, uid, [('is_secretariat', '=', True),
                      ('power_level_id', 'in', level_for_followers_ids)],
            context=context)
        followers_assemblies_values = self.search_read(
            cr, uid, [('instance_id', 'in', int_instance_ids),
                      ('assembly_category_id', 'in', secretariat_categ_ids)],
            ['partner_id'], context=context)
        partner_ids = []
        for followers_assemblies in followers_assemblies_values:
            partner_ids.append(followers_assemblies['partner_id'][0])

        return partner_ids
