# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AddMembership(models.TransientModel):

    _inherit = "add.membership"

    @api.multi
    def _create_membership_line(self, reference=None):
        """
        Create a new membership line for the partner
        :return: bool
        """
        self.ensure_one()
        membership_obj = self.env["membership.line"]

        reference = membership_obj._generate_membership_reference(
            self.partner_id, self.int_instance_id, ref_date=self.date_from
        )

        reference, self.price = self.env["membership.line"]._prepare_custom_renew(
            reference, self.price
        )

        return super()._create_membership_line(reference)
