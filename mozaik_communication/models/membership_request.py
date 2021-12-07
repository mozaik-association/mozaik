# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    distribution_list_ids = fields.Many2many(
        comodel_name="distribution.list",
        relation="membership_request_distribution_list_rel",
        column1="request_id",
        column2="list_id",
        string="Newsletters",
        domain=[("newsletter", "=", True)],
    )

    request_type = fields.Selection(selection_add=[("n", "Other")])

    def validate_request(self):
        self.ensure_one()
        res = super(MembershipRequest, self).validate_request()
        self.distribution_list_ids.write(
            {
                "opt_in_ids": [(4, self.partner_id.id)],
                "opt_out_ids": [(3, self.partner_id.id)],
            }
        )
        return res

    @api.model
    def _onchange_partner_id_vals(
        self, is_company, request_type, partner_id, technical_name
    ):
        """
        Keep Other as request type when the partner is a company
        """
        res = super(MembershipRequest, self)._onchange_partner_id_vals(
            is_company, request_type, partner_id, technical_name
        )

        if is_company and request_type == "n":
            res["value"]["request_type"] = "n"

        return res
