# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from .res_partner import AVAILABLE_PARTNER_KINDS


class email_coordinate(orm.Model):

    _name = 'email.coordinate'
    _inherit = ['sub.abstract.coordinate', 'email.coordinate']

    _int_instance_store_trigger = {
        'email.coordinate': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['email.coordinate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _partner_kind_store_trigger = {
        'email.coordinate': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['email.coordinate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        [
                            'is_assembly', 'is_company',
                            'identifier', 'membership_state_id'
                        ], 12),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
        'partner_kind': fields.related(
            'partner_id', 'kind', string='Partner Kind',
            type='selection', selection=AVAILABLE_PARTNER_KINDS,
            store=_partner_kind_store_trigger),
    }
