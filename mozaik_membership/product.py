# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields


class product_template(orm.Model):

    _inherit = ['product.template']

    def _get_default_subscription(self, cr, uid, context=None):
        """
        =========================
        _get_default_subscription
        =========================
        return id of a default membership product
        """
        return self.pool['ir.model.data'].\
            get_object_reference(cr, uid, 'mozaik_membership',
                                 'membership_product_isolated')[1]

    _columns = {
        'membership': fields.boolean(
            'Subscription',
            help='Check if the product is eligible for membership.'),
    }

# orm methods

    def _register_hook(self, cr):
        super(product_template, self)._register_hook(cr)
        self._fields['name'].track_visibility = 'onchange'
        self._fields['list_price'].track_visibility = 'onchange'
        pass
