# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class int_assembly_category(orm.Model):

    _name = 'int.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = "Internal Assembly Category"

    _columns = {
        'is_secretariat': fields.boolean("Is Secretariat",
                                         track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level',
                                          'Internal Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
    }

    _order = 'power_level_id, name'

    _unicity_keys = 'power_level_id, name'
