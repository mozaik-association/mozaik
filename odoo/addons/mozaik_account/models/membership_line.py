# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
from odoo import api, fields, models, tools, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class MembershipLine(models.Model):
    _inherit = 'membership.line'

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Account move",
        readonly=True,
        copy=False,
        track_visibility='onchange',
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
    price_paid = fields.Float()

    @api.model
    def _get_min_reconciliation_date(self):
        min_date_from = datetime.date.today().replace(day=1, month=1)
        param = self.env["ir.config_parameter"].get_param(
            "membership.allow.reconcile.last.year", default="0")
        if param != "0":
            min_date_from = min_date_from.replace(year=min_date_from.year - 1)
        return fields.Date.to_string(min_date_from)

    @api.model
    @tools.ormcache('reference', 'raise_exception')
    def _get_membership_line_by_ref(self, reference, raise_exception=True):
        """
        Get a membership.line based on given reference.
        As the reference is unique, we can put the result in cache to avoid
        multi-search
        :param reference: str
        :return: self recordset
        """
        domain = [
            ('reference', '=', reference),
        ]
        membership = self.search(domain, limit=1)
        min_date_from = self._get_min_reconciliation_date()
        if membership and membership.date_from < min_date_from:
            if raise_exception:
                raise UserError(_(
                    "The membership you want to reconcile is too old"))
            return self.browse()
        return membership

    @api.model
    def _get_membership_line_by_partner_amount(self, partner, amount,
                                               raise_exception=True):
        precision = self._fields.get('price').digits[1]
        memberships = partner.membership_line_ids.filtered(
            lambda s: not s.paid and not float_compare(
                s.price, amount, precision_digits=precision))
        if len(memberships) > 1:
            raise UserError(_(
                "More than one membership to reconcile are available"))
        min_date_from = self._get_min_reconciliation_date()
        if memberships and memberships.date_from < min_date_from:
            if raise_exception:
                raise UserError(_(
                    "The membership you want to reconcile is too old"))
            return self.browse()
        return memberships

    @api.model
    @tools.ormcache('reference')
    def _get_product_by_ref(self, reference):
        """
        Get a product from the line related to the given reference
        As the reference is unique, we can put the result in cache to avoid
        multi-search
        :param reference: str
        :return: self recordset
        """
        return self._get_membership_line_by_ref(reference).product_id

    @api.multi
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
            raise UserError(
                _("The membership %s is already paid") % self.display_name)
        self.write({
            'paid': True,
            'price_paid': amount,
            'move_id': move_id,
            'bank_account_id': bank_id,
        })
        return self

    @api.model
    def _get_paid_based_on_price(self, price):
        """
        Based on the given price, set the default value for the paid bool
        :param price: float
        :return: bool
        """
        return self.price_is_zero(price)

    @api.model
    def _build_membership_values(
            self, partner, instance, state,
            date_from=False, previous=False, product=False, price=None,
            reference=None):
        """
        Add paid boolean to values
        """
        vals = super()._build_membership_values(
            partner, instance, state,
            date_from=date_from, previous=previous,
            product=product, price=price, reference=reference)
        vals['paid'] = self._get_paid_based_on_price(vals.get('price', 0.0))
        return vals

    @api.model
    def _update_domain_payment(self, domain, inverse=False):
        """

        :param domain: list
        :param inverse: bool
        :return: list (domain)
        """
        domain = domain or []
        value = self.env['ir.config_parameter'].sudo().get_param(
            'membership.renew_must_paid', default='1')
        if value not in [True, 1, '1', 'True']:
            return domain
        operator = '='
        if inverse:
            operator = '!='
        domain.append(('paid', operator, True))
        return domain

    @api.multi
    def _renew(self, date_from=False):
        self.clear_caches()
        return super()._renew(date_from=date_from)

    @api.model
    def _get_lines_to_renew_domain(self, force_lines=None):
        res = super()._get_lines_to_renew_domain(force_lines=force_lines)
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
    def _get_lines_to_close_former_member_domain(self):
        res = super()._get_lines_to_close_former_member_domain()
        return self._update_domain_payment(res, inverse=True)

    @api.model
    def _prepare_custom_renew(self, reference, price):
        """
        make sure that no membership exist with the same reference
        """
        membership = self.env["membership.line"].search([
            ("reference", "=", reference),
            ("active", "=", False),
        ])
        if membership:
            if any(membership.mapped("paid")):
                reference = False
                price = 0
            else:
                membership.write({"reference": False})
        else:
            reference = None
        return reference, price
