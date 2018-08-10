# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sta_assembly_category(orm.Model):

    _name = 'sta.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = 'State Assembly Category'

    _columns = {
        'power_level_id': fields.many2one('sta.power.level',
                                          'State Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
        'is_legislative': fields.boolean('Legislative',
                                         track_visibility='onchange')
    }

    _defaults = {
        'is_legislative': False,
    }

    _order = 'power_level_id, name'

    _unicity_keys = 'power_level_id, name'
