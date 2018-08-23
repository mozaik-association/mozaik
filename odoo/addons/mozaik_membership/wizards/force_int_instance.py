# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class force_int_instance(orm.TransientModel):

    _name = 'force.int.instance'
    _description = 'Change Internal Instance'

    _columns = {
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance',
            required=True),
        'partner_id': fields.many2one(
            'res.partner', string='Partner'),
    }
    _defaults = {
        'partner_id': lambda self, cr, uid, context:
            context.get('active_id', False)
    }

    def force_int_instance_action(self, cr, uid, ids, context=None):
        '''
        update partner internal instance
        '''
        for wiz in self.browse(cr, uid, ids, context=context):
            if wiz.int_instance_id.id != wiz.partner_id.int_instance_id.id:
                partner_id = wiz.partner_id.id
                partner_obj = self.pool['res.partner']
                partner_obj._change_instance(
                    cr, uid, partner_id, wiz.int_instance_id.id,
                    context=context)

        return True
