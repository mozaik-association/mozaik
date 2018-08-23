# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
import openerp.addons.decimal_precision as dp


class membership_line(orm.Model):

    _name = 'membership.line'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership Line'
    _unicity_keys = 'partner_id'
    _rec_name = 'partner_id'
    _order = 'date_from desc, date_to desc, create_date desc, partner_id'

    _int_instance_store_trigger = {
        'membership.line': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['membership.line'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', string='Member',
            ondelete='cascade', required=True, select=True),
        'product_id': fields.many2one(
            'product.product', string='Subscription',
            domain="[('membership', '!=', False), ('list_price', '>', 0.0)]",
            select=True),
        'state_id': fields.many2one(
            'membership.state', string='State',
            select=True),
        'state_code': fields.related('state_id', 'code',
                                     string='State Code', type="char",
                                     readonly=True),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance',
            required=True, select=True),
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
        'reference': fields.char('Reference'),

        'date_from': fields.date('From', readonly=True),
        'date_to': fields.date('To', readonly=True),
        'price': fields.float(
            'Price', digits_compute=dp.get_precision('Product Price'),
            help='Amount of the membership'),
    }

    _defaults = {
        'product_id': lambda self, cr, uid, ids, context = None:
            self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'mozaik_membership', 'membership_product_free')[1],
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool.get('int.instance').get_default(cr, uid),
    }

    def _where_calc(self, cr, user, domain, active_test=True, context=None):
        '''
        If active_test is not present into context then
        Read always inactive membership lines
        '''
        if context is None:
            context = {}
        if not context.get('active_test'):
            context = context.copy()
            context['active_test'] = False
        res = super(membership_line, self)._where_calc(
            cr, user, domain, active_test=active_test, context=context)
        return res

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        Returns partner ids linked to membership ids
        Path to partner must be object.partner_id
        :rparam: partner_ids
        :rtype: list of ids
        """
        model_rds = self.browse(cr, uid, ids, context=context)
        partner_ids = []
        for record in model_rds:
            partner_ids.append(record.partner_id.id)
        return partner_ids

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        Invalidates membership lines
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        if 'date_to' not in vals:
            vals['date_to'] = fields.date.today()

        super(membership_line, self).action_invalidate(
            cr, uid, ids, context=context, vals=vals)

        return True
