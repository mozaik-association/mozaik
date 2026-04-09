# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrDepartment(models.Model):

    _inherit = "hr.department"

    address_id = fields.Many2one(
        "res.partner",
        "Work Address",
        compute="_compute_address_id",
        store=True,
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    @api.depends("company_id", "parent_id")
    def _compute_address_id(self):
        for dept in self:
            if dept.parent_id:
                dept.address_id = dept.parent_id.address_id
            else:
                company_address = dept.company_id.partner_id.address_get(["default"])
                dept.address_id = (
                    company_address["default"] if company_address else False
                )
