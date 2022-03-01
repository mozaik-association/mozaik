# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CreateUserFromPartner(models.TransientModel):

    _inherit = "create.user.from.partner"

    instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Internal Instances",
    )

    def create_user_from_partner(self):
        self.ensure_one()
        res = super(CreateUserFromPartner, self).create_user_from_partner()
        partner_id = self._context.get("active_id", False)
        partner = self.env["res.partner"].browse([partner_id])
        partner.int_instance_m2m_ids = self.instance_ids
        return res
