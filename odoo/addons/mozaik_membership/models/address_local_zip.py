# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class address_local_zip(orm.Model):

    _inherit = 'address.local.zip'

    _columns = {
        'int_instance_id': fields.many2one('int.instance', 'Internal Instance',
                                           required=True, select=True,
                                           track_visibility='onchange'),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context=None:
        self.pool.get('int.instance').get_default(cr, uid)
    }
