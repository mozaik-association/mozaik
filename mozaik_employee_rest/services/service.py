# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import AbstractComponent


class BaseEmployeeService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "base.employee.service"
    _collection = "employee.rest.services"
    _expose_model = "hr.employee"

    def _get(self, _id: int):
        record = self.env[self._expose_model].browse(_id)
        if not record.exists():
            raise MissingError(
                _("The record %(model)s %(id)s does not exist")
                % {"model": self._expose_model, "id": _id}
            )
        return record
