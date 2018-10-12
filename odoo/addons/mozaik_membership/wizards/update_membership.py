# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class UpdateMembership(models.TransientModel):
    """
    Wizard used to update a membership.line
    """
    _name = "update.membership"

    membership_line_id = fields.Many2one(
        comodel_name="membership.line",
        string="Membership line",
        required=True,
        ondelete="cascade",
        readonly=True,
        help="Membership line to update",
    )
    update_type = fields.Selection(
        selection=[
            ('instance', 'Instance'),
            ('product', 'Product/Price'),
        ],
        string="Action type",
        default="instance",
        required=True,
    )
    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Instance",
        ondelete="cascade",
        help="Select a new instance for the membership line",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        help="Select a new product for the membership line",
        domain=[('membership', '!=', False)],
    )
    price = fields.Float(
        string="New price",
    )
    reference = fields.Char()

    @api.model
    def default_get(self, fields_list):
        """

        :param fields_list: list of str
        :return: dict
        """
        result = super(UpdateMembership, self).default_get(fields_list)
        membership_model = self.membership_line_id._name
        # Only if the active_model (from context) is the membership one.
        if self.env.context.get('active_model') == membership_model:
            active_id = self.env.context.get('active_id')
            membership = self.membership_line_id.browse(active_id)
            result.update({
                'membership_line_id': active_id,
                # Fill with the next subscription product by default
                'product_id': membership.partner_id.subscription_product_id.id,
                'price': membership.price,
                'reference': membership.reference,
            })
        return result

    @api.multi
    def action_update(self):
        """
        Action to execute the action
        :return: dict
        """
        self.ensure_one()
        if self.update_type == 'instance':
            self._update_instance()
        elif self.update_type == 'product':
            self._update_product_price()
        return {}

    @api.multi
    def _prepare_update_product_price(self):
        """
        Prepare a dictionary ready to use with the write() method
        to update Product/price of a membership line
        :return: dic
        """
        self.ensure_one()
        vals = {
            'product_id': self.product_id.id,
            'price': self.price,
            'reference': self.reference,
        }
        return vals

    @api.multi
    def _update_product_price(self):
        """
        Update product and price on membership.line
        When we're updating the price, we also have to update the reference
        if the price is > 0.
        :return: bool
        """
        self.ensure_one()
        self.product_id.ensure_one()
        if self.membership_line_id.product_id == self.product_id:
            raise exceptions.UserError(
                _("This product is already set on the membership line"))
        vals = self._prepare_update_product_price()
        return self.membership_line_id.write(vals)

    @api.multi
    def _update_instance(self):
        """
        Update int_instance_id on membership.line
        :return: bool
        """
        self.ensure_one()
        self.int_instance_id.ensure_one()
        if self.membership_line_id.int_instance_id == self.int_instance_id:
            raise exceptions.UserError(
                _("This instance is already set on the membership line"))
        return self.membership_line_id.write({
            'int_instance_id': self.int_instance_id.id,
        })

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """
        Onchange for product_id field.
        if the product is set, find the default price
        :return:
        """
        if self.product_id:
            price = self.membership_line_id._get_subscription_price(
                self.product_id,
                instance=self.membership_line_id.int_instance_id,
                partner=self.membership_line_id.partner_id,
            )
            self.price = price

    @api.onchange('price')
    def _onchange_price(self):
        """
        Onchange for price field.
        if the price become 0, remove the reference by default.
        :return:
        """
        membership = self.membership_line_id
        if self.product_id:
            price_zero = membership.price_is_zero(self.price)
            if price_zero:
                self.reference = ''
            else:
                reference = membership._generate_membership_reference(
                    self.membership_line_id.partner_id,
                    self.membership_line_id.int_instance_id)
                self.reference = reference
