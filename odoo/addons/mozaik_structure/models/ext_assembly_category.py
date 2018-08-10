# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class ext_assembly_category(orm.Model):

    _name = 'ext.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = 'External Assembly Category'

    _columns = {
        # Unused field
        'power_level_id': fields.many2one('int.power.level',
                                          'Internal Power Level'),
    }
