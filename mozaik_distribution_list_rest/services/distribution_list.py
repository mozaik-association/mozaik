# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.distribution_list_info import DistributionListInfo
from ..pydantic_models.distribution_list_search_filter import (
    DistributionListSearchFilter,
)


class DistributionListService(Component):
    _inherit = "base.distribution.list.rest.service"
    _name = "distribution.list.rest.service"
    _usage = "distribution_list"
    _expose_model = "distribution.list"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(DistributionListInfo),
    )
    def get(self, _id: int) -> DistributionListInfo:
        distribution_list = self._get(_id)
        return DistributionListInfo.from_orm(distribution_list)

    def _get_search_domain(self, filters):
        domain = []
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.code:
            domain.append(("code", "like", filters.code))
        if filters.newsletter is not None:
            domain.append(("active", "=", filters.newsletter))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(DistributionListSearchFilter),
        output_param=PydanticModelList(DistributionListInfo),
    )
    def search(
        self, distribution_list_search_filter: DistributionListSearchFilter
    ) -> List[DistributionListInfo]:
        domain = self._get_search_domain(distribution_list_search_filter)
        res: List[DistributionListInfo] = []
        for d in self.env["distribution.list"].sudo().search(domain):
            res.append(DistributionListInfo.from_orm(d))
        return res
