# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import List

from odoo import _, fields
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.news_info import NewsInfo
from ..pydantic_models.news_input_filter import NewsInputFilter
from ..pydantic_models.partner_input import PartnerInput


class NewsService(Component):
    _inherit = "base.news.service"
    _name = "news.rest.service"
    _usage = "news"
    _expose_model = "mozaik.news"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        input_param=PydanticModel(PartnerInput),
        output_param=PydanticModel(NewsInfo),
    )
    def get(self, _id: int, partner_input: PartnerInput) -> NewsInfo:
        news = self._get(_id, partner_input.partner_id)
        return NewsInfo.from_orm(news)

    def _search_filter_news(self, filters: NewsInputFilter):
        consultation_date = filters.consultation_date or fields.Date.today()
        domain = [
            ("start_date", "<=", consultation_date),
            "|",
            ("end_date", "=", False),
            ("end_date", ">=", consultation_date),
        ]
        return self.env["mozaik.news"].search(domain)

    def _get_all_allowed_news_for_partner(
        self, partner_id: int, filters: NewsInputFilter
    ) -> List[NewsInfo]:
        # NB: this method must explicitly take partner_id in input
        # as it will be overridden for special authentication
        # mechanisms such as user tokens.
        if not partner_id:
            raise ValidationError(_("No partner is given."))
        all_news = self._search_filter_news(filters)
        allowed_news = all_news._filter_allowed_for_partner(partner_id)
        return [NewsInfo.from_orm(news) for news in allowed_news]

    @restapi.method(
        routes=[(["/get_all_allowed_news"], "GET")],
        input_param=PydanticModel(NewsInputFilter),
        output_param=PydanticModelList(NewsInfo),
    )
    def get_all_allowed_news(
        self,
        input_info: NewsInputFilter,
    ) -> List[NewsInfo]:
        partner_id = input_info.partner_id
        return self._get_all_allowed_news_for_partner(partner_id, input_info)
