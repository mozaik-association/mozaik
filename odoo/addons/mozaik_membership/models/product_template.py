# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class product_template(orm.Model):

    _inherit = ['product.template']

    _columns = {
        'membership': fields.boolean(
            'Subscription',
            help='Check if the product is eligible for membership.'),
    }

    def _get_default_subscription(self, cr, uid, context=None):
        """
        return id of a default membership product
        """
        return self.pool['ir.model.data'].\
            get_object_reference(cr, uid, 'mozaik_membership',
                                 'membership_product_isolated')[1]

    def _register_hook(self, cr):
        super(product_template, self)._register_hook(cr)
        self._fields['name'].track_visibility = 'onchange'
        self._fields['list_price'].track_visibility = 'onchange'
