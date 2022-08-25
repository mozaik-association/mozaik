# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    interest_group_ids = fields.Many2many(
        "interest.group",
        string="Interest Groups",
        compute="_compute_interest_group_ids",
        store=True,
    )

    apply_security_on_interest_groups = fields.Boolean(
        "Apply Security on Interest Groups",
        help="If ticked, user can see only partners having same interest groups",
    )
    interest_group_user_ids = fields.Many2many(
        comodel_name="interest.group",
        string="Interest Groups for Associated User",
        relation="res_partner_interest_group_manager",
        column1="partner_id",
        column2="interest_group_id",
    )

    @api.depends(
        "partner_involvement_ids",
        "partner_involvement_ids.involvement_category_id",
        "partner_involvement_ids.involvement_category_id.interest_group_ids",
    )
    def _compute_interest_group_ids(self):
        for rec in self:
            rec.interest_group_ids = rec.partner_involvement_ids.mapped(
                "involvement_category_id.interest_group_ids"
            )
