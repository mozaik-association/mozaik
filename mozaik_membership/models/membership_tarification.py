# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class MembershipTarification(models.Model):
    """
    Model to represents the dynamic members tarification
    """

    _name = "membership.tarification"
    _description = "Membership tarification"
    _order = "sequence"

    name = fields.Char(
        help="Name of the tarification",
        required=True,
    )
    sequence = fields.Integer(
        help="Order in which rule will be evaluated",
    )
    code = fields.Char(
        help="Python code to evaluate; should return a boolean.\n"
        "Example of code: partner.is_customer == True",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        domain=[("membership", "=", True)],
    )
    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        ("unique_name", "unique(name)", "This name already exists"),
    ]

    def _get_eval_context(self, partner):
        """
        Get the context for the safe_eval
        :param partner: res.partner recordset
        :return:
        """
        values = {
            "context": self.env.context.copy(),
            "partner": partner,
            "uid": self.env.uid,
            "user": self.env.user,
            "self": self,
            "today": fields.Date.today(),
            "membership_request": (
                self.env.context.get("membership_request_id")
                and self.env["membership.request"].search(
                    [("id", "=", self.env.context.get("membership_request_id"))]
                )
            )
            or False,
        }
        return values

    def _evaluate_code(self, partner):
        """
        Evaluate the code of current recordset
        :param partner: res.partner recordset
        :return: bool
        """
        values = self._get_eval_context(partner=partner)
        result = safe_eval(self.code, values)
        return bool(result)

    @api.model
    def _get_product_by_partner(self, partner):
        """
        Based on the given partner, find the product tarification
        :param partner: res.partner recordset
        :return: product.product recordset
        """
        rules = self.search(
            [
                ("active", "=", True),
            ],
            order="sequence ASC, id ASC",
        )
        for rule in rules:
            if rule._evaluate_code(partner):
                return rule.product_id
        return self.env["product.product"].browse()
