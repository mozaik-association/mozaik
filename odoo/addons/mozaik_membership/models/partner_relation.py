# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class partner_relation(orm.Model):

    _inherit = ['partner.relation']

    _sbj_int_instance_store_trigger = {
        'partner.relation': (
            lambda self, cr, uid, ids, context=None: ids,
            ['subject_partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['partner.relation'].search(
                            cr, SUPERUSER_ID,
                            [('subject_partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _obj_int_instance_store_trigger = {
        'partner.relation': (
            lambda self, cr, uid, ids, context=None: ids,
            ['object_partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['partner.relation'].search(
                            cr, SUPERUSER_ID,
                            [('object_partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'subject_instance_id': fields.related(
            'subject_partner_id', 'int_instance_id',
            string='Subject Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_sbj_int_instance_store_trigger),
        'object_instance_id': fields.related(
            'object_partner_id', 'int_instance_id',
            string='Object Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_obj_int_instance_store_trigger),
    }
