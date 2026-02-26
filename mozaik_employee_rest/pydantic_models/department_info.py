# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List, Optional

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import BaseModel, Field  # pylint:disable=W7936

from odoo.addons.pydantic import utils

from .department_ref import DepartmentRef
from .employee_ref import EmployeeRef


class DepartmentInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    manager: Optional[EmployeeRef] = Field(None, alias="manager_id")
    parent: Optional[DepartmentRef] = Field(None, alias="parent_id")
    children: List[DepartmentRef] = Field(default=[], alias="child_ids")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
