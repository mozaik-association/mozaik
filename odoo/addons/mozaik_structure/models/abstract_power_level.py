# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


class abstract_power_level(orm.AbstractModel):

    _name = 'abstract.power.level'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Power Level'

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'sequence': fields.integer('Sequence',
                                   required=True,
                                   track_visibility='onchange',
                                   group_operator='min'),
        'assembly_category_ids': fields.one2many(
            'abstract.assembly.category',
            'power_level_id',
            'Assembly Categories',
            domain=[('active', '=', True)]),
        'assembly_category_inactive_ids': fields.one2many(
            'abstract.assembly.category',
            'power_level_id',
            'Assembly Categories',
            domain=[('active', '=', False)]),
    }

    _order = 'sequence, name'

    _defaults = {
        'sequence': 5,
    }

    _unicity_keys = 'name'
