# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.website_domain_info import WebsiteDomainInfo
from ..pydantic_models.website_domain_search_filter import WebsiteDomainSearchFilter


class WebsiteDomainService(Component):
    _inherit = "base.petition.rest.service"
    _name = "website.domain.rest.service"
    _usage = "website_domain"
    _expose_model = "website.domain"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(WebsiteDomainInfo),
    )
    def get(self, _id: int) -> WebsiteDomainInfo:
        website_domain = self._get(_id)
        return WebsiteDomainInfo.from_orm(website_domain)

    def _get_search_domain(self, filters):
        domain = []
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.id:
            domain.append(("id", "=", filters.id))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(WebsiteDomainSearchFilter),
        output_param=PydanticModelList(WebsiteDomainInfo),
    )
    def search(
        self, website_domain_search_filter: WebsiteDomainSearchFilter
    ) -> List[WebsiteDomainInfo]:
        domain = self._get_search_domain(website_domain_search_filter)
        res: List[WebsiteDomainInfo] = []
        for e in self.env["website.domain"].sudo().search(domain):
            res.append(WebsiteDomainInfo.from_orm(e))
        return res
