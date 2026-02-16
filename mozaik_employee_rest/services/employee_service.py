# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math

from odoo import _
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel
from odoo.addons.component.core import Component

from ..pydantic_models.employee_detail import EmployeeDetail
from ..pydantic_models.employee_info import EmployeeInfo
from ..pydantic_models.employee_list_response import EmployeeListResponse
from ..pydantic_models.employee_search_filter import EmployeeSearchFilter

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 50


class EmployeeService(Component):
    _inherit = "base.employee.service"
    _name = "employee.rest.service"
    _usage = "employee"
    _description = "Employee REST service"

    def _image_url(self, emp_id: int) -> str or None:
        host_url = request.httprequest.host_url
        if not host_url or not emp_id:
            return None
        return f"{host_url}web/image_api/hr.employee/{emp_id}/image_1920"

    def _build_domain(self, filters: EmployeeSearchFilter):
        domain = []

        if filters.name:
            domain.append(("name", "ilike", filters.name))

        if filters.job_title:
            domain.append(("job_title", "ilike", filters.job_title))

        if filters.job_name:
            domain.append(("job_id.name", "ilike", filters.job_name))

        if filters.category_names:
            # Employee has at least one category whose name is in category_names
            domain.append(("category_ids.name", "in", filters.category_names))

        if filters.department_name:
            domain.append(("department_id.name", "ilike", filters.department_name))

        if filters.parent_id:
            domain.append(("parent_id", "=", filters.parent_id))

        if filters.mobile_phone:
            domain.append(("mobile_phone", "ilike", filters.mobile_phone))

        return domain

    @restapi.method(
        routes=[(["/get"], "GET")],
        input_param=PydanticModel(EmployeeSearchFilter),
        output_param=PydanticModel(EmployeeListResponse),
    )
    def get(self, filters: EmployeeSearchFilter) -> EmployeeListResponse:
        # Pagination defaults
        page = filters.page or DEFAULT_PAGE
        page_size = filters.page_size or DEFAULT_PAGE_SIZE

        if page < 1:
            raise ValidationError(_("page must be >= 1"))
        if page_size < 1:
            raise ValidationError(_("page must be >= 1"))

        domain = self._build_domain(filters)

        Employee = self.env["hr.employee"].sudo()
        total = Employee.search_count(domain)

        offset = (page - 1) * page_size
        employees = Employee.search(
            domain, offset=offset, limit=page_size, order="id asc"
        )

        pages = math.ceil(total / page_size) if page_size else 1

        results = [EmployeeInfo.from_orm(emp) for emp in employees]

        return EmployeeListResponse(
            count=total,
            page=page,
            page_size=page_size,
            pages=pages,
            results=results,
        )

    @restapi.method(
        routes=[(["/get/<int:_id>"], "GET")],
        output_param=PydanticModel(EmployeeDetail),
    )
    def get_by_id(self, _id: int) -> EmployeeDetail:
        emp = self._get(_id)

        data = EmployeeDetail.from_orm(emp)
        # Add image URL
        data.image_1920_url = self._image_url(emp.id)
        return data
