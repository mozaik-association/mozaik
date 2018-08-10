# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID


class abstract_assembly_category(orm.AbstractModel):

    _name = 'abstract.assembly.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Assembly Category'

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'duration': fields.integer('Duration of Mandates',
                                   track_visibility='onchange'),
        'months_before_end_of_mandate': fields.integer(
            'Alert Delay (#Months)',
            track_visibility='onchange', group_operator='min'),
        'power_level_id': fields.many2one('abstract.power.level',
                                          'Power Level'),
    }

    _order = 'name'

    _unicity_keys = 'name'
