# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import first
from odoo.tools import float_compare


class MembershipLine(models.Model):
    _inherit = "membership.line"

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Account move",
        readonly=True,
        copy=False,
        tracking=True,
    )
    donation_move_ids = fields.Many2many(
        comodel_name="account.move",
        string="Donations",
        readonly=True,
        copy=False,
    )
    bank_account_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Bank account",
        readonly=True,
        copy=False,
    )
    paid = fields.Boolean(
        default=False,
        help="Define if this line is paid or not",
        copy=False,
        readonly=True,
    )
    price_paid = fields.Float(copy=False)
    regularization_date = fields.Date(readonly=True)

    def _get_reference(self):
        self.ensure_one()
        res = super(MembershipLine, self)._get_reference()
        if self.paid:
            return False
        return res

    @api.model
    def _get_min_reconciliation_date(self):
        min_date_from = datetime.date.today().replace(day=1, month=1)
        param = self.env["ir.config_parameter"].get_param(
            "membership.allow.reconcile.last.year", default="0"
        )
        if param != "0":
            min_date_from = min_date_from.replace(year=min_date_from.year - 1)
        return min_date_from

    @api.model
    def _get_membership_line_by_ref(self, reference, raise_exception=True):
        """
        Get a membership.line based on given reference.
        As the reference is unique, we can put the result in cache to avoid
        multi-search
        :param reference: str
        :return: self recordset
        """
        domain = [
            ("reference", "=", reference),
        ]
        membership = self.search(domain, limit=1)
        if not membership:
            partner = self.env["res.partner"].search(
                [("stored_reference", "=", reference)]
            )
            membership = first(partner.membership_line_ids.filtered(lambda s: s.active))
        min_date_from = self._get_min_reconciliation_date()
        if (
            membership
            and membership.state_code == "member"
            and membership.date_from < min_date_from
        ):
            if raise_exception:
                raise UserError(_("The membership you want to reconcile is too old"))
            return self.browse()
        return membership

    @api.model
    def _get_membership_line_by_partner_amount(
        self, partner, amount, raise_exception=True
    ):
        precision = self._fields.get("price").get_digits(self.env)[1]
        memberships = partner.membership_line_ids.filtered(
            lambda s: not s.paid
            and not float_compare(s.price, amount, precision_digits=precision)
        )
        if len(memberships) > 1:
            raise UserError(_("More than one membership to reconcile are available"))
        min_date_from = self._get_min_reconciliation_date()
        if memberships and memberships.date_from < min_date_from:
            if raise_exception:
                raise UserError(_("The membership you want to reconcile is too old"))
            return self.browse()
        return memberships

    def _mark_as_paid(self, amount, move_id, bank_id=False):
        """
        Mark as paid current recordset
        Can be inherited to create new lines if any
        :param amount: float
        :param move_id: id of move
        :return: self
        """
        self.ensure_one()
        if self.paid:
            vals = {
                "price_paid": self.price_paid + amount,
            }
            if self.move_id.id != move_id and move_id not in self.donation_move_ids.ids:
                vals["donation_move_ids"] = [(4, move_id, 0)]
            self.write(vals)
        else:
            product = self.env["product.product"].search(
                [
                    ("membership", "=", True),
                    ("list_price", "=", amount),
                ],
                limit=1,
            )
            vals = {
                "paid": True,
                "price_paid": amount,
                "move_id": move_id,
                "bank_account_id": bank_id,
            }

            param_value = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("membership.allow_update_product", default="0")
            )
            if (
                product
                and param_value in [True, 1, "1", "True"]
                or product.list_price > self.price
            ):
                vals["product_id"] = product
                vals["price"] = product.list_price
            self.write(vals)
        return self

    @api.model
    def _get_new_member_free_renew_state(self):
        return self.env.ref("mozaik_membership.member_committee")

    @api.model
    def _get_free_condition(self, nb_exemption_months, partner, date_from):
        new_membership = self.env["membership.line"].search_count(
            [
                ("state_id", "in", self._get_new_member_free_renew_state().ids),
                ("partner_id", "=", partner.id),
                (
                    "date_from",
                    ">=",
                    fields.Date.from_string(date_from)
                    - relativedelta(months=nb_exemption_months),
                ),
            ]
        )
        return new_membership and all(
            m.paid for m in partner.membership_line_ids if m.date_from < date_from
        )

    def _update_membership_values(self, partner, instance, state, date_from):
        self.ensure_one()
        nb_month = int(
            self.env["ir.config_parameter"].get_param(
                "membership.nb_month_exemption", default="2"
            )
        )
        vals = super()._update_membership_values(partner, instance, state, date_from)
        if self._get_free_condition(nb_month, partner, date_from):
            vals["paid"] = True
            vals["price"] = 0
        return vals

    @api.model
    def _build_membership_values(
        self,
        partner,
        instance,
        state,
        date_from=False,
        product=False,
        price=None,
        reference=None,
    ):
        """
        Add paid boolean to values
        """
        vals = super()._build_membership_values(
            partner,
            instance,
            state,
            date_from=date_from,
            product=product,
            price=price,
            reference=reference,
        )
        vals["paid"] = self._price_is_zero(vals.get("price", 0.0))
        return vals

    @api.model
    def _update_domain_payment(self, domain, inverse=False):
        """

        :param domain: list
        :param inverse: bool
        :return: list (domain)
        """
        domain = domain or []
        value = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("membership.renew_must_paid", default="1")
        )
        if value not in [True, 1, "1", "True"]:
            return domain
        operator = "="
        if inverse:
            operator = "!="
        domain.append(("paid", operator, True))
        return domain

    @api.model
    def _get_lines_to_renew_domain(self, force_lines=None, ref_date=None):
        res = super()._get_lines_to_renew_domain(
            force_lines=force_lines, ref_date=ref_date
        )
        return self._update_domain_payment(res)

    @api.model
    def _get_lines_to_former_member_domain(self):
        res = super()._get_lines_to_former_member_domain()
        return self._update_domain_payment(res, inverse=True)

    @api.model
    def _get_lines_to_close_renew_domain(self):
        res = super()._get_lines_to_close_renew_domain()
        return self._update_domain_payment(res)

    @api.model
    def _get_lines_to_close_domain(self):
        res = super()._get_lines_to_close_domain()
        return self._update_domain_payment(res, inverse=True)

    @api.model
    def _prepare_custom_renew(self, reference, price):
        """
        make sure that no membership exist with the same reference
        """
        membership = self.env["membership.line"].search(
            [
                ("reference", "=", reference),
                ("active", "=", False),
            ]
        )
        if membership:
            if any(membership.mapped("paid")):
                reference = False
                price = 0
            else:
                membership.write({"reference": False})
                membership.flush()
        return reference, price

    @api.model
    def create(self, vals):
        if vals.get("paid", False):
            vals["regularization_date"] = fields.Date.today()
        return super().create(vals)

    def write(self, vals):
        if vals.get("paid"):
            vals["regularization_date"] = fields.Date.today()
        elif not vals.get("paid", True):
            vals["regularization_date"] = False
        return super().write(vals)
