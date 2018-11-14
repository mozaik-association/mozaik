# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
    )
    paid = fields.Boolean(
        default=False,
        help="Define if this line is paid or not",
        copy=False,
        readonly=True,
    )

    @api.model
    @tools.ormcache('reference')
    def _get_membership_line_by_ref(self, reference):
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
        return self.search(domain, limit=1)

    @api.model
    def _get_membership_line_by_partner_amount(self, partner, amount):
        precision = self._fields.get('price').digits[1]
        memberships = partner.membership_line_ids.filtered(
            lambda s: s.active and not s.move_id and not float_compare(
                s.price, amount, precision_digits=precision))
        if len(memberships) > 1:
            raise UserError(_(
                "There are more than one membership available to reconciled"))
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
    def _mark_as_paid(self, amount, move_id):
        """
        Mark as paid current recordset
        Can be inherited to create new lines if any
        :param amount: float
        :param move_id: id of move
        :return: self
        """
        self.ensure_one()
        self.write({
            'paid': True,
            'price': amount,
            'move_id': move_id,
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
            date_from=False, previous=False, product=False, price=None):
        """
        Add paid boolean to values
        """
        vals = super()._build_membership_values(
            partner, instance, state,
            date_from=date_from, previous=previous,
            product=product, price=price)
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

    @api.model
    def _get_lines_to_renew_domain(self):
        res = super()._get_lines_to_renew_domain()
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
