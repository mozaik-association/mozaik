# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List, Optional

import pydantic  # pylint:disable=W7936
from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936


class EmployeeSearchFilter(pydantic.BaseModel, metaclass=ExtendableModelMeta):
    # Pagination
    page: int = pydantic.Field(1, description="Page number (>= 1)")
    page_size: int = pydantic.Field(50, description="Page size (>= 1)")

    # Filters
    name: Optional[str] = None
    job_title: Optional[str] = None
    job_name: Optional[str] = None
    category_names: Optional[List[str]] = None
    department_name: Optional[str] = None
    parent_id: Optional[int] = None
    mobile_phone: Optional[str] = None
