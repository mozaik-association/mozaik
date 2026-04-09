# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployeeBase(models.AbstractModel):

    _inherit = "hr.employee.base"

    @api.depends("department_id", "department_id.address_id")
    def _compute_address_id(self):
        res = super()._compute_address_id()
        for employee in self.filtered("department_id"):
            if employee.department_id.address_id:
                employee.address_id = employee.department_id.address_id
        return res
