# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    distribution_list_ids = fields.Many2many(
        comodel_name="distribution.list",
        relation="membership_request_distribution_list_rel",
        column1="request_id",
        column2="list_id",
        string="Newsletters (opt-in)",
        domain=[("newsletter", "=", True)],
    )

    distribution_list_ids_opt_out = fields.Many2many(
        comodel_name="distribution.list",
        relation="membership_request_distribution_list_opt_out_rel",
        column1="request_id",
        column2="list_id",
        string="Newsletters (opt-out)",
        domain=[("newsletter", "=", True)],
    )

    request_type = fields.Selection(selection_add=[("n", "Other")])

    @api.constrains("distribution_list_ids", "distribution_list_ids_opt_out")
    def _check_distribution_list_ids(self):
        """
        The same distribution.list cannot be inside both fields
        distribution_list_ids and distribution_list_ids_opt_out.
        """
        for record in self:
            if set(record.distribution_list_ids.ids).intersection(
                set(record.distribution_list_ids_opt_out.ids)
            ):
                raise ValidationError(
                    _(
                        "You cannot add the same newsletter "
                        "to newsletters (opt-in) and newsletters (opt-out)."
                    )
                )

    def validate_request(self):
        """
        Update opt-in / opt-out subscriptions on distribution lists.
        Set the postal bounced back to False if address was changed.
        """
        self.ensure_one()
        res = super(MembershipRequest, self).validate_request()
        if self.address_id:
            self.partner_id.write({"last_postal_failure_date": False})
        self.distribution_list_ids.write(
            {
                "res_partner_opt_in_ids": [(4, self.partner_id.id)],
                "res_partner_opt_out_ids": [(3, self.partner_id.id)],
            }
        )
        self.distribution_list_ids_opt_out.write(
            {
                "res_partner_opt_out_ids": [(4, self.partner_id.id)],
                "res_partner_opt_in_ids": [(3, self.partner_id.id)],
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
