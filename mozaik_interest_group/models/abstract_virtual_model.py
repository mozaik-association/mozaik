# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AbstractVirtualModel(models.AbstractModel):

    _inherit = "abstract.virtual.model"

    partner_interest_group_ids = fields.Many2many(
        comodel_name="interest.group",
        string="Partner Interest Groups",
        compute="_compute_partner_interest_group_ids",
        search="_search_partner_interest_group_ids",
    )

    def _compute_partner_instance_ids(self):
        self._compute_custom_related(
            "partner_interest_group_ids", "partner_id.interest_group_ids"
        )

    def _search_partner_interest_group_ids(self, operator, value):
        """
        We implement a search method since we will need to search on
        partner_interest_group_ids in record rules.
        """
        if operator not in [
            "in",
            "not in",
            "child_of",
            "ilike",
            "not ilike",
            "=",
            "!=",
        ]:
            raise ValueError(_("This operator is not supported"))
        if operator in ["ilike", "not ilike"] and not isinstance(value, str):
            raise ValueError(_("value should be a string"))
        if operator in ["=", "!="] and not (
            isinstance(value, str) or isinstance(value, bool)
        ):
            raise ValueError(_("value should either be a string or a boolean"))
        if operator in ["in", "not in", "child of"] and not isinstance(value, list):
            raise ValueError(_("value should be a list"))
        auth_partners = self.env["res.partner"].search(
            [("interest_group_ids", operator, value)]
        )
        return [("partner_id", "in", auth_partners.ids)]
