# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Optional

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import BaseModel, Field  # pylint:disable=W7936

from odoo.addons.pydantic import utils

from .employee_ref import EmployeeRef


class DepartmentRef(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    manager: Optional[EmployeeRef] = Field(None, alias="manager_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
