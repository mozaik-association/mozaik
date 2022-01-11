# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.fields import first
from odoo.tools import float_compare


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("partner_id"):
                __, partner = self._get_info_from_reference(vals.get("payment_ref"))
                if partner:
                    vals["partner_id"] = partner.id
        return super().create(vals_list)

    @api.model
    def _get_models(self):
        return {
            "res.partner": {"mode": "partner", "map": lambda s: s},
            "membership.line": {"mode": "membership", "map": "partner_id"},
            "partner.involvement": {"mode": "donation", "map": "partner_id"},
        }

    @api.model
    def _get_info_from_reference(self, reference):
        """
        Get the mode and the partner associated to a given reference
        """
        if not reference:
            return False, False

        domain = [
            ("reference", "=", reference),
            ("active", "<=", True),
        ]

        models_mode = self._get_models()
        for model in models_mode:
            obj = (
                self.env[model]
                .search(domain)
                .mapped(models_mode.get(model, {}).get("map"))
            )
            if obj:
                return models_mode.get(model, {}).get("mode"), first(obj)

        return False, False

    def _create_donation_move(self, reference):
        """
        Create an account move related to a donation
        """
        self.ensure_one()
        line_count = self.search_count([("payment_ref", "=", reference)])
        if line_count > 1:
            # do not auto reconcile if reference has already been used
            return

        prod_id = self.env.ref("mozaik_account.product_template_donation")

        account = prod_id.product_tmpl_id._get_product_accounts().get("income")
        if account:
            move_dicts = [
                {
                    "account_id": account.id,
                    "debit": 0,
                    "credit": self.amount,
                    "name": reference,
                }
            ]
            self.process_reconciliation(new_aml_dicts=move_dicts)

    def _propagate_payment(self, vals):
        self.ensure_one()
        memb_obj = self.env["membership.line"]
        amount_paid = vals.get("credit") or 0.0
        reference = vals.get("name") or ""
        mode, partner = self._get_info_from_reference(reference)
        if mode == "membership":
            move_id = vals.get("move_id", False)
            membership = memb_obj._get_membership_line_by_ref(reference)
            bank_account_id = self.partner_bank_id.id
            membership._mark_as_paid(amount_paid, move_id, bank_account_id)
        if mode == "partner":
            move_id = vals.get("move_id", False)
            bank_account_id = self.partner_bank_id.id
            partner.pay_membership(amount_paid, move_id, bank_account_id)

        if mode == "donation":
            involvements = self.env["partner.involvement"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("reference", "=", reference),
                    ("active", "<=", True),
                ]
            )
            if involvements:
                vals = {
                    "effective_time": self.date,
                    "amount": amount_paid,
                }
                involvements.write(vals)

        # try to find if a membership have the same amount for the partner
        partner_id = vals.get("partner_id")
        if not mode and partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            membership = memb_obj._get_membership_line_by_partner_amount(
                partner, amount_paid
            )
            if membership and not membership.paid:
                move_id = vals.get("move_id", False)
                bank_account_id = self.partner_bank_id.id
                membership._mark_as_paid(amount_paid, move_id, bank_account_id)
        return

    def _create_membership_move_from_partner(self, raise_exception=True):
        self.ensure_one()
        memb_obj = self.env["membership.line"]
        partner = self.partner_id
        amount_paid = self.amount
        membership = memb_obj._get_membership_line_by_partner_amount(
            partner, amount_paid, raise_exception=raise_exception
        )
        self._reconcile_membership_move(membership)

    def _create_membership_move(self, reference, raise_exception=True):
        """
        Method to create account move linked to membership payment
        """
        self.ensure_one()
        membership = self.env["membership.line"]._get_membership_line_by_ref(
            reference, raise_exception=raise_exception
        )
        self._reconcile_membership_move(membership)

    def _reconcile_membership_move(self, membership):
        self.ensure_one()
        if membership.paid:
            return
        product = membership.product_id
        account = product.property_subscription_account
        precision = membership._fields.get("price").get_digits(self.env)[1]
        # float_compare return 0 if values are equals
        cmp = float_compare(self.amount, membership.price, precision_digits=precision)
        product = self.env["product.product"].search(
            [
                ("membership", "=", True),
                ("list_price", "=", self.amount),
            ],
            limit=1,
        )
        param_value = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("membership.allow_update_product", default="0")
        )
        if account and (not cmp or product and param_value in [True, 1, "1", "True"]):
            move_dicts = [
                {
                    "account_id": account.id,
                    "debit": 0,
                    "credit": self.amount,
                    "name": membership.reference,
                }
            ]
            self.process_reconciliation(new_aml_dicts=move_dicts)

    @api.model
    def _get_available_account_reconciliation(self):
        subscription_product = self.env["product.product"].search(
            [("membership", "=", True)]
        )
        subscription_accounts = subscription_product.mapped(
            "property_subscription_account"
        )
        donation_p = self.env.ref("mozaik_account.product_template_donation")
        return subscription_accounts | donation_p.property_account_income_id

    def process_reconciliation(
        self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None
    ):
        if self.filtered(lambda l: not l.partner_id):
            raise ValidationError(_("You must first select a partner!"))

        for aml in new_aml_dicts:
            name = aml.get("name")
            if name:
                aml["name"] = name.strip()

        res = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts,
        )

        if new_aml_dicts:
            reconcilable_accounts = self._get_available_account_reconciliation()

            for data in new_aml_dicts:
                if data["account_id"] in reconcilable_accounts.ids:
                    self._propagate_payment(data)
        return res

    def _auto_reconcile(self):
        reconciled_lines = self.env["account.bank.statement.line"]
        for bank_line in self.filtered(
            lambda l: not (not l.partner_id or l.is_reconciled)
        ):
            mode, __ = bank_line._get_info_from_reference(bank_line.payment_ref)
            if mode in ["membership", "partner"]:
                bank_line._create_membership_move(
                    bank_line.payment_ref, raise_exception=False
                )
            elif mode == "donation":
                bank_line._create_donation_move(bank_line.payment_ref)
            elif not mode:
                bank_line._create_membership_move_from_partner(raise_exception=False)
            if bank_line.is_reconciled:
                reconciled_lines += bank_line
        return reconciled_lines

    def reconciliation_widget_auto_reconcile(self, num_already_reconciled_lines):
        reconciled_lines = self._auto_reconcile()
        num_already_reconciled_lines += len(reconciled_lines)
        return super(
            AccountBankStatementLine, self - reconciled_lines
        ).reconciliation_widget_auto_reconcile(num_already_reconciled_lines)
