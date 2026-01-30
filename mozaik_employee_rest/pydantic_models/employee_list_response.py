# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import BaseModel  # pylint:disable=W7936

from .employee_info import EmployeeInfo


class EmployeeListResponse(BaseModel, metaclass=ExtendableModelMeta):
    count: int
    page: int
    page_size: int
    pages: int
    results: List[EmployeeInfo]
