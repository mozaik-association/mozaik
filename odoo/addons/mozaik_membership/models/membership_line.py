# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
import odoo.addons.decimal_precision as dp


class MembershipLine(models.Model):

    _name = 'membership.line'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership Line'
    _rec_name = 'partner_id'
    _order = 'date_from desc, date_to desc, create_date desc, partner_id'
    _unicity_keys = 'partner_id'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Member',
        ondelete='cascade', required=True, index=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Subscription',
        domain="[('membership', '!=', False), ('list_price', '>', 0.0)]",
        index=True, default=lambda s: s._default_product_id())
    state_id = fields.Many2one(
        comodel_name='membership.state', string='State',
        index=True)
    state_code = fields.Char(related='state_id.code', readonly=True)
    int_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Internal Instance', index=True,
        default=lambda s: s._default_int_instance_id(), required=True,)
    partner_instance_id = fields.Many2one(
        related='partner_id.int_instance_id',
        string='Partner Internal Instance',
        comodel_name='int.instance',
        index=True, readonly=True, store=True)
    reference = fields.Char()
    date_from = fields.Date(string='From', readonly=True)
    date_to = fields.Date(string='To', readonly=True)
    price = fields.Float(
        digits=dp.get_precision('Product Price'))

    @api.model
    def _default_product_id(self):
        return self.env.ref('mozaik_membership.membership_product_free')

    @api.model
    def _default_int_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()

    @api.model
    def _where_calc(self, domain, active_test=True):
        '''
        Read always inactive membership lines
        '''
        return super()._where_calc(domain, active_test=False)

    @api.multi
    def action_invalidate(self, vals=None):
        """
        Invalidates membership lines
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        if 'date_to' not in vals:
            vals['date_to'] = fields.date.today()

        return super().action_invalidate(vals=vals)
