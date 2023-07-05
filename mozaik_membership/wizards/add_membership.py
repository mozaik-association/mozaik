# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.fields import first


class AddMembership(models.TransientModel):
    """
    Wizard used to create a new membership.line
    """

    _name = "add.membership"
    _description = "Wizard to create a new membership"

    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Instance",
        required=True,
        ondelete="cascade",
        help="Select a new instance for the membership line",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        readonly=True,
        ondelete="cascade",
        help="Partner to affiliate",
    )
    date_from = fields.Date(
        help="Start of subscription",
        default=lambda s: fields.Date.today(),
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Subscription",
        domain=[("membership", "=", True)],
    )
    price = fields.Float(
        help="Subscription price",
    )
    state_id = fields.Many2one(
        comodel_name="membership.state",
        string="State",
        required=True,
        domain=lambda self: self._get_state_domain(),
    )
    state_code = fields.Char(related="state_id.code", readonly=True)
    is_excluded = fields.Boolean(
        help="Checked if the partner is currently excluded",
        related="partner_id.is_excluded",
        readonly=True,
    )

    can_display_product_price = fields.Boolean(
        compute="_compute_can_display_product_price"
    )

    @api.model
    def _get_states_can_display_product_price(self):
        """
        Return the list of states for which the price and product
        can be set on the membership line.
        This corresponds to states for which the product/price can be updated
        via the button on the membership line, once created.
        """
        return self.env["membership.line"]._get_states_can_update_product()

    @api.depends("state_code")
    def _compute_can_display_product_price(self):
        allowed_states = self._get_states_can_display_product_price()
        for wiz in self:
            wiz.can_display_product_price = self.state_code in allowed_states

    @api.model
    def _get_state_domain(self):
        """

        :return: domain for membership.state
        """
        return []

    @api.model
    def default_get(self, fields_list):
        """

        :param fields_list: list of str
        :return: dict
        """
        result = super(AddMembership, self).default_get(fields_list)
        # Only if the active_model is res.partner
        partner_model = self.partner_id._name
        if self.env.context.get("active_model") == partner_model:
            active_id = self.env.context.get("active_id")
            partner = self.env[self.partner_id._name].browse()
            instance = self.int_instance_id
            if active_id:
                partner = partner.browse(active_id)
                instance = partner.force_int_instance_id
            # Subscription product defined on the partner or
            # the last one used into membership lines
            product = partner.subscription_product_id
            if not product:
                membership = first(partner.membership_line_ids)
                product = membership.product_id
            result.update(
                {
                    "partner_id": partner.id,
                    "int_instance_id": instance.id,
                    "product_id": product.id,
                }
            )
        return result

    @api.onchange("partner_id", "state_code")
    def _onchange_partner_id(self):
        """
        Onchange for partner_id field.
        If the partner is set, update the default product with the product
        defined on the partner (subscription_product_id)
        :return:
        """
        if self.partner_id and self.state_code == "member":
            self.product_id = self.partner_id.subscription_product_id
        else:
            self.product_id = False

    @api.onchange("product_id", "int_instance_id")
    def _onchange_product_id(self):
        """
        Onchange for product_id field.
        if the product is set, find the default price
        :return:
        """
        if self.product_id:
            price = self.env["membership.line"]._get_subscription_price(
                self.product_id, partner=self.partner_id, instance=self.int_instance_id
            )
            self.price = price
        else:
            self.price = 0

    def action_add(self):
        """
        Action to create the membership line for the partner
        :return: membership.line
        """
        self.ensure_one()
        return self._create_membership_line()

    def _create_membership_line(self, reference=None):
        """
        Create a new membership line for the partner
        :return: bool
        """
        self.ensure_one()
        membership_obj = self.env["membership.line"]
        values = membership_obj._build_membership_values(
            self.partner_id,
            self.int_instance_id,
            self.state_id,
            date_from=self.date_from,
            product=self.product_id,
            price=self.price,
            reference=reference,
        )
        active_membership = self.env["membership.line"].search(
            [
                ("int_instance_id", "=", self.int_instance_id.id),
                ("active", "=", True),
                ("partner_id", "=", self.partner_id.id),
            ]
        )
        if active_membership:
            active_membership._close(date_to=self.date_from, force=True)
        res = membership_obj.create(values)
        # We need to flush to trigger the re-compute
        # before erasing the value of the previous membership state
        res.flush()
        res.partner_id.previous_membership_state_id = False
        return res
