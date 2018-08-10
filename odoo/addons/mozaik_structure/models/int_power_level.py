# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields

from openerp.tools import SUPERUSER_ID


class int_power_level(orm.Model):

    _name = 'int.power.level'
    _inherit = ['abstract.power.level']
    _description = 'Internal Power Level'

    _columns = {
        'assembly_category_ids': fields.one2many(
            'int.assembly.category',
            'power_level_id',
            'Internal Assembly Categories',
            domain=[('active', '=', True)]
        ),
        'assembly_category_inactive_ids': fields.one2many(
            'int.assembly.category',
            'power_level_id',
            'Internal Assembly Categories',
            domain=[('active', '=', False)]
        ),
        'level_for_followers': fields.boolean('Level For Followers'),
    }

    _defaults = {
        'level_for_followers': False,
    }

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Power Level
        """
        res_id = self.pool['ir.model.data'].xmlid_to_res_id(
            cr, SUPERUSER_ID, 'mozaik_structure.int_power_level_01')
        return res_id
