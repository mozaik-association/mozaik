# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.event_website_domain_info import EventWebsiteDomainInfo
from ..pydantic_models.event_website_domain_search_filter import (
    EventWebsiteDomainSearchFilter,
)


class EventWebsiteDomainService(Component):
    _inherit = "base.event.rest.service"
    _name = "event.website.domain.rest.service"
    _usage = "event_website_domain"
    _expose_model = "event.website.domain"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(EventWebsiteDomainInfo),
    )
    def get(self, _id: int) -> EventWebsiteDomainInfo:
        event_website_domain = self._get(_id)
        return EventWebsiteDomainInfo.from_orm(event_website_domain)

    def _get_search_domain(self, filters):
        domain = []
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.id:
            domain.append(("id", "=", filters.id))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(EventWebsiteDomainSearchFilter),
        output_param=PydanticModelList(EventWebsiteDomainInfo),
    )
    def search(
        self, event_website_domain_search_filter: EventWebsiteDomainSearchFilter
    ) -> List[EventWebsiteDomainInfo]:
        domain = self._get_search_domain(event_website_domain_search_filter)
        res: List[EventWebsiteDomainInfo] = []
        for e in self.env["event.website.domain"].sudo().search(domain):
            res.append(EventWebsiteDomainInfo.from_orm(e))
        return res
