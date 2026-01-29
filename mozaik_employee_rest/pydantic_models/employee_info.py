# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List, Optional

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import BaseModel, Field  # pylint:disable=W7936

from odoo.addons.pydantic import utils

from .category_info import CategoryInfo
from .department_info import DepartmentInfo
from .employee_ref import EmployeeRef
from .job_info import JobInfo


class EmployeeInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    job_title: Optional[str] = None

    job: Optional[JobInfo] = Field(None, alias="job_id")
    categories: List[CategoryInfo] = Field(default=[], alias="category_ids")
    department: Optional[DepartmentInfo] = Field(None, alias="department_id")

    parent: Optional[EmployeeRef] = Field(None, alias="parent_id")
    mobile_phone: Optional[str] = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
