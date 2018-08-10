# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sta_power_level(orm.Model):

    _name = 'sta.power.level'
    _inherit = ['abstract.power.level']
    _description = 'State Power Level'

    _columns = {
        'assembly_category_ids': fields.one2many('sta.assembly.category',
                                                 'power_level_id',
                                                 'Assembly Categories'),
        'assembly_category_inactive_ids': fields.one2many(
            'sta.assembly.category',
            'power_level_id',
            'Assembly Categories',
            domain=[
                ('active', '=', False)
            ]),
    }
